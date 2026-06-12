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
    


class topoDragonFly(Topo):
    def __init__(self):
        Topo.__init__(self)
        self.topoKeys = ["topology", "debug", "num_ports", "flit_size", "link_bw", "xbar_bw", "dragonfly.hosts_per_router", "dragonfly.routers_per_group", "dragonfly.intergroup_per_router", "dragonfly.num_groups","dragonfly.intergroup_links","input_latency","output_latency","input_buf_size","output_buf_size","dragonfly.global_route_mode"]
        self.topoOptKeys = ["xbar_arb","link_bw.host","link_bw.group","link_bw.global","input_latency.host","input_latency.group","input_latency.global","output_latency.host","output_latency.group","output_latency.global","input_buf_size.host","input_buf_size.group","input_buf_size.global","output_buf_size.host","output_buf_size.group","output_buf_size.global","num_vns","vn_remap","vn_remap_shm","portcontrol.output_arb","portcontrol.arbitration.qos_settings","portcontrol.arbitration.arb_vns","portcontrol.arbitration.arb_vcs"]
        self.global_link_map = None
        self.global_routes = "absolute"

    def getName(self):
        return "Dragonfly"

    def prepParams(self):
#        if "xbar_arb" not in _params:
#            _params["xbar_arb"] = "merlin.xbar_arb_lru"
        _params["topology"] = "merlin.dragonfly"
        _params["debug"] = debug
#        _params["router_radix"] = int(_params["router_radix"])
        _params["dragonfly.hosts_per_router"] = int(_params["dragonfly.hosts_per_router"])
        _params["dragonfly.routers_per_group"] = int(_params["dragonfly.routers_per_group"])
        _params["dragonfly.intergroup_links"] = int(_params["dragonfly.intergroup_links"])
        _params["dragonfly.num_groups"] = int(_params["dragonfly.num_groups"])
        _params["num_peers"] = _params["dragonfly.hosts_per_router"] * _params["dragonfly.routers_per_group"] * _params["dragonfly.num_groups"]
        _params["dragonfly.global_route_mode"] = self.global_routes


        self.total_intergroup_links = (_params["dragonfly.num_groups"] - 1) * _params["dragonfly.intergroup_links"]
        _params["dragonfly.intergroup_per_router"] = int((self.total_intergroup_links + _params["dragonfly.routers_per_group"] - 1 ) // _params["dragonfly.routers_per_group"])
        self.empty_ports = _params["dragonfly.intergroup_per_router"] * _params["dragonfly.routers_per_group"] - self.total_intergroup_links

        _params["router_radix"] = _params["dragonfly.routers_per_group"]-1 + _params["dragonfly.hosts_per_router"] + _params["dragonfly.intergroup_per_router"]
        _params["num_ports"] = int(_params["router_radix"])

        if _params["dragonfly.num_groups"] > 2:
            foo = _params["dragonfly.algorithm"]
            self.topoKeys.append("dragonfly.algorithm")

    def setGlobalLinkMap(self, glm):
        self.global_link_map = glm

    def setRoutingModeAbsolute(self):
        self.global_routes = "absolute"

    def setRoutingModeRelative(self):
        self.global_routes = "relative"


    def getRouterNameForId(self,rtr_id):
        rpg = _params["dragonfly.routers_per_group"]
        ret = self.getRouterNameForLocation(rtr_id // rpg, rtr_id % rpg)
        return ret

    def getRouterNameForLocation(self,group,rtr):
        return "rtr_G%dR%d"%(group,rtr)

    def findRouterByLocation(self,group,rtr):
        return sst.findComponentByName(self.getRouterNameForLocation(group,rtr))


    def get_global_link_map(self):
        if self.global_link_map is None:
            self.calculate_global_link_map()
        return self.global_link_map

    def calculate_global_link_map(self):
        '''
        
        '''
        intergroup_per_router = _params["dragonfly.intergroup_per_router"]
        routers_per_group = _params["dragonfly.routers_per_group"]
        intergroup_per_group = intergroup_per_router * routers_per_group
        self.global_link_map = [-1 for i in range(intergroup_per_group)]

        # Links will be mapped in linear order, but we will
        # potentially skip one port per router, depending on the
        # parameters.  The variable self.empty_ports tells us how
        # many routers will have one global port empty.
        count = 0
        start_skip = routers_per_group - self.empty_ports
        for rtr_idx in range(0,routers_per_group):
            # Determine if we skip last port for this router
            end = intergroup_per_router
            if rtr_idx >= start_skip:
                end = end - 1
            for j in range(0,end):
                self.global_link_map[rtr_idx*intergroup_per_router+j] = count;
                count = count + 1
    
    def global_router_idx(self, group_num, router_idx_in_group):
        return group_num * _params["dragonfly.routers_per_group"] + router_idx_in_group

    def rank_local_groups(self):
        my_rank = _params['my_rank']
        groups_per_rank = max(1, _params["dragonfly.num_groups"] // _params['rank_count'])
        
        my_group_start = my_rank * groups_per_rank
        my_group_end = my_group_start + groups_per_rank
        if my_rank == _params['rank_count'] - 1:
            my_group_end = _params["dragonfly.num_groups"]
        
        for group_idx in range(my_group_start, my_group_end):
            yield group_idx

    def group_idx_to_rank(self, group_idx):
        groups_per_rank = max(1, _params["dragonfly.num_groups"] // _params['rank_count'])
        return min(group_idx // groups_per_rank, _params['rank_count'] - 1)

    def ig_router_indices(self, group_src, group_dst):
        '''
        Given two group indices, return the group-local router indices that connect those two groups. The returned `(rtr_idx1, rtr_idx2)` means that the intergroup link between `group_src` and `group_dst` connects router `rtr_idx1` in `group_src` to router `rtr_idx2` in `group_dst`.
        '''
        if group_src == group_dst:
            log(0, 'Error: ig_router_indices should not be called with the same group as source and destination')
            return ()
        
        # Maximum amount of intergroup links that may be on a single router. For example, with ng=6, nr=2, within each group, one router will have 3 intergroup links and the other will have 2. 
        intergroup_links_per_router = max(1, _params['dragonfly.num_groups'] // _params['dragonfly.routers_per_group'])

        if self.global_routes == 'absolute':
            if group_src < group_dst:
                rtr_dst = group_src // intergroup_links_per_router
                rtr_src = (group_dst - 1) // intergroup_links_per_router
            else:
                rtr_dst = (group_src - 1) // intergroup_links_per_router
                rtr_src = group_dst // intergroup_links_per_router
            return (rtr_src, rtr_dst)
    
        if self.global_routes == 'relative':
            if group_src < group_dst:
                rtr_src = (group_dst - group_src - 1) // intergroup_links_per_router
                rtr_dst = (group_src - group_dst + self._params['dragonfly.num_groups'] - 1) // intergroup_links_per_router
            else:
                rtr_src = (group_dst - group_src + self._params['dragonfly.num_groups'] - 1) // intergroup_links_per_router
                rtr_dst = (group_src - group_dst - 1) // intergroup_links_per_router
            return (rtr_src, rtr_dst)
    

    def rank_ghost_routers(self):
        global_link_map = self.get_global_link_map()
        for local_group_idx in self.rank_local_groups():
            for dst_grp_idx in range(0, self._params["dragonfly.num_groups"]):
                if dst_grp_idx == local_group_idx:
                    continue
                (_, rtr_idx_dst) = self.ig_router_indices(local_group_idx, dst_grp_idx)
                yield (dst_grp_idx, rtr_idx_dst)        
        
    def build_take2(self):
        my_rank = _params['my_rank']
        links = dict()
        def get_link(name):
            if name not in links:
                links[name] = sst.Link(name)
            return links[name]
        
        
        routers_per_group = _params["dragonfly.routers_per_group"]
        num_groups = _params["dragonfly.num_groups"]
        intergroup_per_router = _params["dragonfly.intergroup_per_router"]

        if self.global_link_map is None:
             self.calculate_global_link_map()
            
        log(0, "Global link map array: %s"%(self.global_link_map))

        # Given router `router_idx` in group `group_idx` and global port index `global_port_idx` (which ranges from 0 to intergroup_per_router-1), return the link that connects that port to a router in another group.
        def get_global_link(group_idx, router_idx, global_port_idx):
            assert(global_port_idx < intergroup_per_router)
            glm = self.get_global_link_map()
            raw_dest = glm[router_idx * intergroup_per_router + global_port_idx]
            if raw_dest == -1:
                return None

            # Turn raw_dest into dest_grp and link_num
            link_num = raw_dest // num_groups;
            dest_grp = raw_dest - link_num * num_groups

            if ( self.global_routes == "absolute" ):
                # Compute dest group ignoring my own group id, for a
                # dest_grp >= g, we need to add 1 to get the right group
                if dest_grp >= group_idx:
                    dest_grp = dest_grp + 1
            elif ( self.global_routes == "relative"):
                # For relative, add current group to dest_grp + 1 and
                # do modulo of num_groups to get actual group
                dest_grp = (dest_grp + group_idx + 1) % (num_groups+1)

            src = min(dest_grp, group_idx)
            dest = max(dest_grp, group_idx)
            return get_link("link_g%dg%dr%d"%(src,dest,link_num))
        
        swap_keys = [("dragonfly.hosts_per_router","hosts_per_router"),("dragonfly.routers_per_group","routers_per_group"),("dragonfly.intergroup_links","intergroup_links"),("dragonfly.num_groups","num_groups"),("dragonfly.intergroup_per_router","intergroup_per_router"),("dragonfly.algorithm","algorithm"),("dragonfly.global_route_mode","global_route_mode"),("dragonfly.adaptive_threshold","adaptive_threshold")]
        _topo_params = _params.subsetWithRename(swap_keys);
    
        # Create and connect local routers
        for my_grp_idx in self.rank_local_groups():

            for router_num in range(routers_per_group):
                global_rtr_idx = self.global_router_idx(my_grp_idx, router_num)

                log(0, f'creating router {router_num} for group {my_grp_idx} with global index {global_rtr_idx}')
                rtr = self._instanceRouter(global_rtr_idx, "merlin.hr_router")
                rtr.setRank(my_rank)
                rtr.addParams(_params.subset(self.topoKeys, self.topoOptKeys))
                rtr.addParam("id", global_rtr_idx)
                topology = rtr.setSubComponent("topology","merlin.dragonfly")
                topology.addParams(_topo_params)
                # Not sure why this is only being added once in the original build method.
                # Probably need to sort out how to add it to all ranks once, but will come to that later
                if global_rtr_idx == 0:
                    # Need to send in the global_port_map
                    rtr.addParam("dragonfly.global_link_map",self.global_link_map)
                    topology.addParam("global_link_map",self.global_link_map)

                # Create and add endpoint components
                port = 0
                for p in range(_params["dragonfly.hosts_per_router"]):
                    ep = self._getEndPoint(nic_num).build(nic_num, {})
                    ep.setRank(my_rank)
                    if ep:
                        ep.setRank(my_rank)
                        link = sst.Link("link_g%dr%dh%d"%(my_grp_idx, global_rtr_idx, p))
                        if self.bundleEndpoints:
                            link.setNoCut()
                        link.connect(ep, (rtr, "port%d"%port, _params["link_lat"]) )
                    nic_num = nic_num + 1
                    port = port + 1
                
                # Create links within this group
                for p in range(_params["dragonfly.routers_per_group"]):
                    if p != router_num:
                        src = min(p,router_num)
                        dst = max(p,router_num)
                        rtr.addLink(get_link("link_g%dr%dr%d"%(my_grp_idx, src, dst)), "port%d"%port, _params["link_lat"])
                        port = port + 1
                
                # Create intergroup links
                for p in range(_params["dragonfly.intergroup_per_router"]):
                    link = get_global_link(my_grp_idx, router_num, p)
                    if link is not None:
                        rtr.addLink(link,"port%d"%port, _params["link_lat"])
                    port = port + 1
            
            # Create the ghost routers this group connects to
            for dst_grp_idx in range(0, num_groups):
                if dst_grp_idx == my_grp_idx or self.group_idx_to_rank(dst_grp_idx) == my_rank:
                    continue
                (local_rtr_idx, dst_rtr_idx) = self.ig_router_indices(my_grp_idx, dst_grp_idx)
                dst_rtr_global_idx = self.global_router_idx(dst_grp_idx, dst_rtr_idx)
                log(0, 'creating ghost router for dst group %d, dst rtr idx %d'%(dst_grp_idx, dst_rtr_idx))
                ghost_rtr = self._instanceRouter(dst_rtr_global_idx, "merlin.hr_router")
                
                ghost_rtr.addParam("id", dst_rtr_global_idx)
                ghost_rtr.addParams(_params.subset(self.topoKeys, self.topoOptKeys))
                ghost_rtr.setRank(self.group_idx_to_rank(dst_grp_idx))
                topology = ghost_rtr.setSubComponent("topology","merlin.dragonfly")
                topology.addParams(_topo_params)
                # Skipping subcomponents as its a ghost router

                # Add its connection to the local router
                # Need: ghost router's port number for this connection
                port_num = -1
                for p in range(_params["dragonfly.intergroup_per_router"]):
                    if self.get_global_link_map()[dst_rtr_idx * intergroup_per_router + p] == my_grp_idx:
                        port_num = p
                        break
                assert(port_num != -1)
                link = get_global_link(dst_grp_idx, dst_rtr_idx, port_num)
                ghost_rtr.addLink(link, "port%d"%port_num, _params["link_lat"])




                


    def build(self):
        links = dict()

        #####################
        def getLink(name):
            if name not in links:
                links[name] = sst.Link(name)
            return links[name]
        #####################

        rpg = _params["dragonfly.routers_per_group"]
        ng = _params["dragonfly.num_groups"] - 1 # don't count my group
        igpr = _params["dragonfly.intergroup_per_router"]

        if self.global_link_map is None:
            # Need to define global link map

            self.global_link_map = [-1 for i in range(igpr * rpg)]

            # Links will be mapped in linear order, but we will
            # potentially skip one port per router, depending on the
            # parameters.  The variable self.empty_ports tells us how
            # many routers will have one global port empty.
            count = 0
            start_skip = rpg - self.empty_ports
            for i in range(0,rpg):
                # Determine if we skip last port for this router
                end = igpr
                if i >= start_skip:
                    end = end - 1
                for j in range(0,end):
                    self.global_link_map[i*igpr+j] = count;
                    count = count + 1

        #print("Global link map array")
        #print(self.global_link_map)

        # End set global link map with default


        # g is group number
        # r is router number with group
        # p is port number relative to start of global ports on this router

        def getGlobalLink(g, r, p):
            # Look into global link map to get the dest group and link
            # number to that group
            raw_dest = self.global_link_map[r * igpr + p];
            if raw_dest == -1:
                return None

            # Turn raw_dest into dest_grp and link_num
            link_num = raw_dest // ng;
            dest_grp = raw_dest - link_num * ng

            if ( self.global_routes == "absolute" ):
                # Compute dest group ignoring my own group id, for a
                # dest_grp >= g, we need to add 1 to get the right group
                if dest_grp >= g:
                    dest_grp = dest_grp + 1
            elif ( self.global_routes == "relative"):
                # For relative, add current group to dest_grp + 1 and
                # do modulo of num_groups to get actual group
                dest_grp = (dest_grp + g + 1) % (ng+1)
            #else:
                # should never happen

            src = min(dest_grp, g)
            dest = max(dest_grp, g)

            #getLink("link:g%dg%dr%d"%(g, src, dst)), "port%d"%port, _params["link_lat"])
            return getLink("link_g%dg%dr%d"%(src,dest,link_num))

        #########################

        swap_keys = [("dragonfly.hosts_per_router","hosts_per_router"),("dragonfly.routers_per_group","routers_per_group"),("dragonfly.intergroup_links","intergroup_links"),("dragonfly.num_groups","num_groups"),("dragonfly.intergroup_per_router","intergroup_per_router"),("dragonfly.algorithm","algorithm"),("dragonfly.global_route_mode","global_route_mode"),("dragonfly.adaptive_threshold","adaptive_threshold")]

        _topo_params = _params.subsetWithRename(swap_keys);

        router_num = 0
        nic_num = 0
        # GROUPS
        for g in range(_params["dragonfly.num_groups"]):

            # GROUP ROUTERS
            for r in range(_params["dragonfly.routers_per_group"]):
                rtr = self._instanceRouter(router_num,"merlin.hr_router")
                #rtr = sst.Component("rtr:G%dR%d"%(g, r), "merlin.hr_router")
                rtr.addParams(_params.subset(self.topoKeys, self.topoOptKeys))
                rtr.addParam("id", router_num)
                topology = rtr.setSubComponent("topology","merlin.dragonfly")
                topology.addParams(_topo_params)
                if router_num == 0:
                    # Need to send in the global_port_map
                    #map_str = str(self.global_link_map).strip('[]')
                    #rtr.addParam("dragonfly.global_link_map",map_str)
                    rtr.addParam("dragonfly.global_link_map",self.global_link_map)
                    topology.addParam("global_link_map",self.global_link_map)

                port = 0
                for p in range(_params["dragonfly.hosts_per_router"]):
                    ep = self._getEndPoint(nic_num).build(nic_num, {})
                    if ep:
                        link = sst.Link("link_g%dr%dh%d"%(g, r, p))
                        if self.bundleEndpoints:
                            link.setNoCut()
                        link.connect(ep, (rtr, "port%d"%port, _params["link_lat"]) )
                    nic_num = nic_num + 1
                    port = port + 1

                for p in range(_params["dragonfly.routers_per_group"]):
                    if p != r:
                        src = min(p,r)
                        dst = max(p,r)
                        rtr.addLink(getLink("link_g%dr%dr%d"%(g, src, dst)), "port%d"%port, _params["link_lat"])
                        port = port + 1

                for p in range(_params["dragonfly.intergroup_per_router"]):
                    link = getGlobalLink(g,r,p)
                    if link is not None:
                        rtr.addLink(link,"port%d"%port, _params["link_lat"])
                    port = port +1

                router_num = router_num +1




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
