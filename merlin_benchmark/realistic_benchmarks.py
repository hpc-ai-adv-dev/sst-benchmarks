import itertools
import sys
import sst


class Params(dict):
    def __missing__(self, key):
        print("Please enter %s: "%key)
        val = input()
        self[key] = val
        return val
    def subset(self, keys, optKeys = []):
        ret = dict((k, self[k]) for k in keys)
        #ret.update(dict((k, self[k]) for k in (optKeys and self)))
        for k in optKeys:
            if k in self:
                ret[k] = self[k]
        return ret
    def subsetWithRename(self, keys):
        ret = dict()
        for k,nk in keys:
            if k in self:
                ret[nk] = self[k]
        return ret
    # Needed to avoid asking for input when a key isn't present
#    def optional_subset(self, keys):
#        return

_params = Params()

_params['my_rank'] = sst.getMyMPIRank()
_params['rank_count'] = sst.getMPIRankCount()
_params['thread_count'] = sst.getThreadCount()

debug=0

def log(lvl, *args):
    if debug >= lvl:
        print('Rank %d: '%(_params['my_rank']), *args)


class Topo(object):
    def __init__(self):
        self.topoKeys = []
        self.topoOptKeys = []
        self.bundleEndpoints = True
        def epFunc(epID):
            return None
        self._getEndPoint = epFunc
    def keepEndPointsWithRouter(self):
        self.bundleEndpoints = False
    def getName(self):
        return "NoName"
    def prepParams(self):
        pass
    def setEndPoint(self, endPoint):
        def epFunc(epID):
            return endPoint
        self._getEndPoint = epFunc
    def setEndPointFunc(self, epFunc):
        self._getEndPoint = epFunc
    def build(self):
        pass
    def getRouterNameForId(self,rtr_id):
        return "rtr_%d"%rtr_id
    def findRouterById(self,rtr_id):
        return sst.findComponentByName(self.getRouterNameForId(rtr_id))
    def _instanceRouter(self,rtr_id,rtr_type):
        log(0, f'_instanceRouter({rtr_id}, {rtr_type})')
        name = self.getRouterNameForId(rtr_id)
        log(0, f'returning sst.Component({name, rtr_type})')
        return sst.Component(self.getRouterNameForId(rtr_id),rtr_type)


class topoMesh(Topo):
    def __init__(self):
        Topo.__init__(self)
        self.topoKeys = ["topology", "debug", "num_ports", "flit_size", "link_bw", "xbar_bw", "mesh.shape", "mesh.width", "mesh.local_ports","input_latency","output_latency","input_buf_size","output_buf_size"]
        self.topoOptKeys = ["xbar_arb","num_vns","vn_remap","vn_remap_shm","portcontrol.output_arb","portcontrol.arbitration.qos_settings","portcontrol.arbitration.arb_vns","portcontrol.arbitration.arb_vcs"]
    def getName(self):
        return "Mesh"
    def prepParams(self):
#        if "xbar_arb" not in _params:
#            _params["xbar_arb"] = "merlin.xbar_arb_lru"
        peers = 1
        radix = 0
        self.dims = []
        self.dimwidths = []
        if not "mesh.shape" in _params:
            self.nd = int(_params["num_dims"])
            for x in range(self.nd):
                print("Dim %d size:"%x)
                ds = int(input())
                self.dims.append(ds);
            _params["mesh.shape"] = self._formatShape(self.dims)
        else:
            self.dims = [int(x) for x in _params["mesh.shape"].split('x')]
            self.nd = len(self.dims)
        if not "mesh.width" in _params:
            for x in range(self.nd):
                print("Dim %d width (# of links in this dimension):" % x)
                dw = int(input())
                self.dimwidths.append(dw)
            _params["mesh.width"] = self._formatShape(self.dimwidths)
        else:
            self.dimwidths = [int(x) for x in _params["mesh.width"].split('x')]

        local_ports = int(_params["mesh.local_ports"])
        radix = local_ports + 2 * sum(self.dimwidths)

        for x in self.dims:
            peers = peers * x
        peers = peers * local_ports

        _params["num_peers"] = peers
        _params["num_dims"] = self.nd
        _params["topology"] = _params["topology"] = "merlin.mesh"
        _params["debug"] = debug
        _params["num_ports"] = _params["router_radix"] = radix
        _params["mesh.local_ports"] = local_ports

    def _formatShape(self, arr):
        return 'x'.join([str(x) for x in arr])


    def _idToLoc(self,rtr_id):
        foo = list()
        for i in range(self.nd-1, 0, -1):
            div = 1
            for j in range(0, i):
                div = div * self.dims[j]
            value = (rtr_id // div)
            foo.append(value)
            rtr_id = rtr_id - (value * div)
        foo.append(rtr_id)
        foo.reverse()
        return foo
    
    def _locToId(self, rtr_loc):
        rtr_id = 0
        for i in range(self.nd-1, -1, -1):
            rtr_id = rtr_id * self.dims[i]
            rtr_id = rtr_id + rtr_loc[i]
        return rtr_id

    def getRouterNameForId(self,rtr_id):
        return self.getRouterNameForLocation(self._idToLoc(rtr_id))

    def getRouterNameForLocation(self,location):
        return "rtr_%s"%(self._formatShape(location))

    def findRouterByLocation(self,location):
        return sst.findComponentByName(self.getRouterNameForLocation(location));


    def _router_loc_to_rank(self, rtr_loc):
        rows_per_rank = max(1,self.dims[0] // _params['rank_count'])
        return min(rtr_loc[0] // rows_per_rank, _params['rank_count'] - 1)
    
    def local_router_indices(self, include_ghosts=False):
        rows_per_rank = max(1,self.dims[0] // _params['rank_count'])
        start_row = rows_per_rank * _params['my_rank']
        end_row = start_row + rows_per_rank
        if _params['my_rank'] == _params['rank_count'] - 1:
            end_row = self.dims[0]
        
        low_ghost_start = max(0, start_row - 1)
        low_ghost_end = start_row
        high_ghost_start = end_row
        high_ghost_end = min(self.dims[0], end_row + 1)

        if include_ghosts:
            for row in range(low_ghost_start, low_ghost_end):
                for remaining_indices in itertools.product(*[range(x) for x in self.dims[1:]]):
                    yield ([row] + list(remaining_indices), True)
        for row in range(start_row, end_row):
            for remaining_indices in itertools.product(*[range(x) for x in self.dims[1:]]):
                yield ([row] + list(remaining_indices), False)
        if include_ghosts:
            for row in range(high_ghost_start, high_ghost_end):
                for remaining_indices in itertools.product(*[range(x) for x in self.dims[1:]]):
                    yield ([row] + list(remaining_indices), True)

    def build(self):
        links=dict()
        def get_link_name(leftName, rightName, num):
            return "link_%s_%s_%d"%(leftName, rightName, num)
        def getLink(leftName, rightName, num):
            name = get_link_name(leftName, rightName, num)
            if name not in links:
                links[name] = sst.Link(name)
            return links[name]
        
        def at_least_one_local(loc1, loc2):
            return self._router_loc_to_rank(loc1) == _params['my_rank'] or \
                   self._router_loc_to_rank(loc2) == _params['']
        
        swap_keys = [("mesh.shape","shape"),("mesh.width","width"),("mesh.local_ports","local_ports")]
        _topo_params = _params.subsetWithRename(swap_keys);
    
        # First, create all the router components, including ghost routers
        for (rtr_loc, is_ghost) in self.local_router_indices(include_ghosts=True):
            rtr_global_id = self._locToId(rtr_loc)
            rtr = self._instanceRouter(rtr_global_id, "merlin.hr_router")
            assert(rtr is not None)

            # Verify we can search it
            found_rtr_by_loc = self.findRouterByLocation(rtr_loc)
            if found_rtr_by_loc is None:
                log(0, f'ERROR: failed to find router by location {rtr_loc}')
            found_rtr_by_id = self.findRouterById(rtr_global_id)
            if found_rtr_by_id is None:
                log(0, f'ERROR: failed to find router by id {rtr_global_id}')
            if found_rtr_by_loc.getFullName() != found_rtr_by_id.getFullName():
                log(0, f'ERROR: found_rtr != found_rtr_by_id: {found_rtr_by_loc.getFullName()} != {found_rtr_by_id.getFullName()}')

            rtr.setRank(self._router_loc_to_rank(rtr_loc))

            # We only need to add parameters and topology for local components
            if not is_ghost:
                rtr.addParams(_params.subset(self.topoKeys, self.topoOptKeys))
                rtr.addParam("id", rtr_global_id)
                topology = rtr.setSubComponent("topology","merlin.mesh")
                topology.addParams(_topo_params)

        # Second, connect routers to their neighbors
        for (rtr_loc,is_ghost) in self.local_router_indices(include_ghosts=True):
            rtr_global_id = self._locToId(rtr_loc)
            mylocstr = self._formatShape(rtr_loc)
            rtr = self.findRouterByLocation(rtr_loc)

            if rtr is None:
                log(0, "Error: Could not find router at location %s (global ID %d)"%(mylocstr, rtr_global_id))
                continue

            port = 0
            for dim in range(self.nd):
                their_loc = rtr_loc[:]

                # Positive direction
                if rtr_loc[dim]+1 < self.dims[dim]:
                    their_loc[dim] = (rtr_loc[dim] +1 ) % self.dims[dim]
                    theirlocstr = self._formatShape(their_loc)
                    for num in range(self.dimwidths[dim]):
                        if at_least_one_local(rtr_loc, their_loc):
                            rtr.addLink(getLink(mylocstr, theirlocstr, num), "port%d"%port, _params["link_lat"])
                        port = port+1
                else:
                    port += self.dimwidths[dim]
                
                # Negative direction
                if rtr_loc[dim] > 0:
                    their_loc[dim] = ((rtr_loc[dim] -1) +self.dims[dim]) % self.dims[dim]
                    theirlocstr = self._formatShape(their_loc)
                    for num in range(self.dimwidths[dim]):
                        if at_least_one_local(rtr_loc, their_loc):
                            rtr.addLink(getLink(theirlocstr, mylocstr, num), "port%d"%port, _params["link_lat"])
                        port = port+1
                else:
                    port += self.dimwidths[dim]

            # We're done for ghost components    
            if is_ghost:
                continue

            # For local components, create the endpoints and link them to the routers
            for local_ep_number in range(_params["mesh.local_ports"]):
                global_ep_number = int(_params["mesh.local_ports"]) * rtr_global_id + local_ep_number
                ep = self._getEndPoint(global_ep_number).build(global_ep_number, {})
                if ep:
                    nic_link = sst.Link("nic_%d_%d"%(rtr_global_id, local_ep_number))
                    if self.bundleEndpoints:
                        nic_link.setNoCut()
                    rtr.addLink(nic_link, "port%d"%port, _params["link_lat"])
                    ep[0].addLink(nic_link, ep[1], ep[2])
                port = port + 1
    


class EndPoint(object):
    def __init__(self):
        self.epKeys = []
        self.epOptKeys = []
        self.enableAllStats = False
        self.statInterval = "0"
    def getName(self):
        print("Not implemented")
        sys.exit(1)
    def prepParams(self):
        pass
    def build(self, nID, extraKeys):
        return None

class TestEndPoint(EndPoint):
    def __init__(self):
        EndPoint.__init__(self)
        #self.enableAllStats = False;
        #self.statInterval = "0"
        #self.nicKeys = ["topology", "num_peers", "num_messages", "link_bw", "checkerboard"]
        self.epKeys.extend(["num_peers", "link_bw"])
        self.epOptKeys.extend(["checkerboard", "num_messages"])
        self.split = 1
        self.group_array = None

    def divide(self,split):
        self.split = split

    def getName(self):
        return "Test End Point"

    def prepParams(self):
        #if "checkerboard" not in _params:
        #    _params["checkerboard"] = "1"
        #if "num_messages" not in _params:
        #    _params["num_messages"] = "10"
        pass

    def build(self, nID, extraKeys):
        # Copmute group size and offset
        if self.group_array is None:
            num_ep = _params["num_peers"]
            min_per_group = num_ep // self.split
            self.group_array = [min_per_group] * self.split
            num_ep = num_ep - ( min_per_group * self.split )
            for i in range(num_ep):
                self.group_array[i] = self.group_array[i] + 1


        nic = sst.Component("testNic_%d"%nID, "merlin.test_nic")
        
        log(0, 'testNic_%d on rank %d'%(nID, _params['my_rank']))

        linkif = nic.setSubComponent("networkIF","merlin.linkcontrol")
        nic.setRank(_params['my_rank'])
        if ( "link_bw" in _params):
            linkif.addParam("link_bw",_params["link_bw"])
        #if ( "input_buf_size" in _params):
        #    linkif.addParam("input_buf_size",_params["input_buf_size"])
        #if ( "output_buf_size" in _params):
        #    linkif.addParam("output_buf_size",_params["output_buf_size"])
        nic.addParams(_params.subset(self.epKeys, self.epOptKeys))
        nic.addParams(_params.subset(extraKeys))
        nic.addParam("id", nID)
        if self.split != 1:
            # Need to figure out what group I'm in
            limit = 0
            offset = 0
            for i in range(self.split):
                limit = limit + self.group_array[i]
                if nID < limit:
                    nic.addParam("group_peers",self.group_array[i])
                    nic.addParam("group_offset",offset)
                    break
                offset = offset + self.group_array[i]
        if self.enableAllStats:
            nic.enableAllStatistics({"type":"sst.AccumulatorStatistic","rate":self.statInterval})
        return (linkif, "rtr_port", _params["link_lat"])
    
    def enableAllStatistics(self,interval):
        self.enableAllStats = True;
        self.statInterval = interval;
