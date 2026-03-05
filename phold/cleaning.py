
import pandas as pd
from plotnine import * 
pd.set_option("display.max_columns", 100)

def parameter_columns(): 
  return ['Experiment Name', 'Node Count', 'Ranks Per Node', 'Thread Count',
       'Width', 'Height', 'Event Density', 'Ring Size', 'Time to Run (ns)',
       'Small Payload (bytes)', 'Large Payload (bytes)',
       'Large Event Fraction', 'Imbalance Factor', 'Component Size']

def varied_parameters(data):
  mask = data[data.columns.intersection(parameter_columns())].nunique() > 1
  return  mask.index[mask].tolist()

def memory_columns():
  return ['Max Local Memory Usage (GiB)',
       'Max Global Memory Usage (GiB)', 'SLURM Allocated Memory (GiB)',
       'Max Local Memory Utilization (%)', 'Max Global Memory Utilization (%)']

  
def measurement_columns():
  return ['Build Time (s)', 'Run Time (s)', 'Max Resident Set Size (bytes)',
       'Max Global Set Size (bytes)', 'Rank Sync Time Max (s)',
       'Rank Sync Time Min (s)', 'Rank Sync Time Mean (s)',
       'Rank Sync Time Std (s)', 'Rank Sync Count Max', 'Rank Sync Count Min',
       'Rank Sync Count Mean', 'Rank Sync Count Std',
       'Thread Sync Time Max (s)', 'Thread Sync Time Min (s)',
       'Thread Sync Time Mean (s)', 'Thread Sync Time Std (s)',
       'Thread Sync Count Max', 'Thread Sync Count Min',
       'Thread Sync Count Mean', 'Thread Sync Count Std',
       'Status']

def calculated_columns():
  return ['Rank Count', 'Total Threads', 'Threads Per Node', 'Components', 'Million Components',
       'Components Per Node', 'Million Components Per Node', 'StencilLength',
       'Total Links', 'Boundary Count', 'Remote Links', 'Remote Links (Ranks)',
       'Remote Link Fraction (%)', 'Remote Link Fraction (%) (Ranks)',
       'Links Per Component', 'Rows Per Node', 'Rows Per Rank',
       'Million Links', 'Links Per Node', 'Million Links Per Node',
       'Average Event Size (bytes)', 'Average Event Size (KiB)',
       'Sync Time Mean (s)', 'Sync Time Max (s)', 'Sync Time Min (s)',
       'Mean Sync Time Fraction (%)', 'Max Sync Time Fraction (%)',
       'Min Sync Time Fraction (%)', 'Event Time Mean (s)', 'Event Count',
       'Events/Second', 'Million Events Per Second',
       'Synchronizations Per Second', 'Max Local Memory Usage (GiB)',
       'Max Global Memory Usage (GiB)', 'SLURM Allocated Memory (GiB)',
       'Max Local Memory Utilization (%)', 'Max Global Memory Utilization (%)',
       'Nodes', 'Density', 'Remote Event Fraction (%)']

def read_all_csvs(directory):
  '''
  Reads all CSV files in the given directory and concatenates them into a single DataFrame.
  '''
  import os
  dataframes = []
  for filename in os.listdir(directory):
    if filename.endswith('.csv'):
      filepath = os.path.join(directory, filename)
      df = pd.read_csv(filepath)
      df['File'] = filename  # Add a column with the filename
      dataframes.append(df)
  
  return pd.concat(dataframes, ignore_index=True)

def triangular(n):
  return n * (n + 1) // 2

   
def total_link_count(ring_size, height, width):
  stencil_length = 2 * ring_size + 1
  total_links = (height * width) * (stencil_length **2)
  total_links -= (height + width) * stencil_length * ring_size * (ring_size + 1)
  total_links += (ring_size * (ring_size + 1)) ** 2
  return total_links

def total_remote_links(ring_size, width, boundary_count):
  '''
  Calculates the total number of remote links in a grid with the given ring size, global width, and boundary count.
  This function assumes that the ring_size is is greater than or equal to the width of each node's portion of the grid.
  '''
  stencil_length = 2 * ring_size + 1
  remote_links = width * stencil_length * ring_size * (ring_size + 1)

  #This needs to account for any ghost remote links off the edge of the grid.
  remote_links -= (ring_size * (ring_size + 1)) ** 2
  return remote_links * boundary_count

def remote_link_fraction(ring_size, height, width, boundary_count):
  total_links = total_link_count(ring_size, height, width)
  remote_links = total_remote_links(ring_size, width, boundary_count)
  return 100 * remote_links / total_links if total_links > 0 else 0

def height_from_fraction(target_fraction, ring_size, width, boundary_count):
  '''
  Calculates the height of the grid needed to get a given remote link target_.
  Fraction should be a percentage (0-100).
  '''
  if target_fraction < 0 or target_fraction > 100:
    raise ValueError("Target Fraction must be between 0 and 100.")
  
  remote_links = total_remote_links(ring_size, width, boundary_count)
  
  total_links = remote_links / (target_fraction / 100)
  # Now we work backwards to the part of the expression containing the height
  stencil_length = 2 * ring_size + 1
  tmp = total_links - (ring_size * (ring_size + 1)) ** 2

  tmp2 = tmp + width * stencil_length * ring_size * (ring_size + 1)

  #tmp2 = height * width * stencilLength ** 2 - height * stencilLength * numRings * (numRings + 1)
  #tmp2 = height * (width * stencilLength ** 2 - stencilLength * numRings * (numRings + 1)
  height = tmp2 / (width * stencil_length ** 2 - stencil_length * ring_size * (ring_size + 1))
  return height

def fill_missing_fields(data):
  if 'Small Payload (bytes)' not in data.columns:
    data['Small Payload (bytes)'] = 0
  if 'Large Payload (bytes)' not in data.columns:
    data['Large Payload (bytes)'] = 0
  if 'Large Event Fraction' not in data.columns:
    data['Large Event Fraction'] = 0
  return data


def mem_based_fields(data):
  data['Max Local Memory Usage (GiB)'] = data['Max Resident Set Size (bytes)'] / (1024.0 ** 3)
  data['Max Global Memory Usage (GiB)'] = data['Max Global Set Size (bytes)'] / (1024.0 ** 3)
  data['SLURM Allocated Memory (GiB)'] = 512.0 * data['Node Count'] # hotlum
  data['Max Local Memory Utilization (%)'] = 100 * data['Max Local Memory Usage (GiB)'] / 512.0
  data['Max Global Memory Utilization (%)'] = 100 * data['Max Global Memory Usage (GiB)'] / data['SLURM Allocated Memory (GiB)']

  return data
def time_based_fields(data):
  if 'Sync Time Mean (s)' not in data.columns:
    data['Sync Time Mean (s)'] = data['Rank Sync Time Mean (s)'] + data['Thread Sync Time Mean (s)']
  if 'Sync Time Max (s)' not in data.columns:
    data['Sync Time Max (s)'] = data['Rank Sync Time Max (s)'] + data['Thread Sync Time Max (s)']
  if 'Sync Time Min (s)' not in data.columns:
    data['Sync Time Min (s)'] = data['Rank Sync Time Min (s)'] + data['Thread Sync Time Min (s)']
  data['Mean Sync Time Fraction (%)'] = 100 * data['Sync Time Mean (s)'] / data['Run Time (s)']
  data['Max Sync Time Fraction (%)'] = 100 * data['Sync Time Max (s)'] / data['Run Time (s)']
  data['Min Sync Time Fraction (%)'] = 100 * data['Sync Time Min (s)'] / data['Run Time (s)']
  
  data['Event Time Mean (s)'] = data['Run Time (s)'] - data['Sync Time Mean (s)']

  data['Event Count'] = data['Time to Run (ns)'] * data['Event Density'] * data['Components']
  data['Events/Second'] = data['Event Count'] / data['Run Time (s)']
  data['Million Events Per Second'] = data['Events/Second'] / 1e6
  data['Synchronizations Per Second'] = data['Time to Run (ns)'] / data['Run Time (s)']
  data['Events/Second Total'] = data['Event Count'] / (data['Run Time (s)'] + data['Build Time (s)'])
  data['Million Events Per Second Total'] = data['Events/Second Total'] / 1e6


  data['SyncFraction'] = '0% to 10%'
  data.loc[data['Mean Sync Time Fraction (%)'] >= 10, 'SyncFraction'] = '10% to 20%'
  data.loc[data['Mean Sync Time Fraction (%)'] >= 20, 'SyncFraction'] = '20% to 30%'
  data.loc[data['Mean Sync Time Fraction (%)'] >= 30, 'SyncFraction'] = '30% to 40%'
  data.loc[data['Mean Sync Time Fraction (%)'] >= 40, 'SyncFraction'] = '40% to 50%'
  data.loc[data['Mean Sync Time Fraction (%)'] >= 50, 'SyncFraction'] = '>50%'
  data.loc[data['Status'] == 'Failure', 'SyncFraction'] = 'Failure'
  
  return data


def topology_fields(data):
  if 'Ranks Per Node' in data.columns:
    data['Rank Count'] = data['Node Count'] * data['Ranks Per Node']
  if 'Thread Count' in data.columns:
    data['Total Threads'] = data['Rank Count'] * data['Thread Count']
    data['Threads Per Node'] = data['Total Threads'] // data['Node Count']


  data['Components'] = data['Width'] * data['Height']
  data['Million Components'] = data['Components'] / 1e6
  data['Components Per Node'] = data['Components'] / data['Node Count']
  data['Million Components Per Node'] = data['Components Per Node'] / 1e6

  # Total Links is counting unidirectional links
  data['StencilLength'] = 2 * data['Ring Size'] + 1

  # start as if each component had a full set of links
  data['Total Links'] = data['Components'] * data['StencilLength'] ** 2

  # Remove the links that aren't there around the edges
  data['Total Links'] -= (data['Height'] + data['Width']) * data['StencilLength'] * data['Ring Size'] * (data['Ring Size'] + 1)

  # Add back the corners of the edges that got counted twice
  data['Total Links'] += (data['Ring Size'] * (data['Ring Size'] + 1)) ** 2


  data['Total Links'] = total_link_count(data['Ring Size'], data['Height'], data['Width'])

  # One less boundary than total nodes
  data['Boundary Count'] = data['Node Count'] - 1

  data['Remote Links'] = total_remote_links(data['Ring Size'], data['Width'], data['Boundary Count'])
  data['Remote Links (Ranks)'] = total_remote_links(data['Ring Size'], data['Width'], data['Rank Count'] - 1)


  data['Remote Link Fraction (%)'] = 100 * data['Remote Links'] / data['Total Links']
  data['Remote Link Fraction (%) (Ranks)'] = 100 * data['Remote Links (Ranks)'] / data['Total Links']


  data['Links Per Component'] = data['Total Links'] / data['Components']
  data['Rows Per Node'] = data['Height'] / data['Node Count']
  data['Rows Per Rank'] = data['Height'] / data['Rank Count']

  data['Million Links'] = data['Total Links'] / 1e6
  data['Links Per Node'] = data['Total Links'] / data['Node Count']
  data['Million Links Per Node'] = data['Links Per Node'] / 1e6

  data['Average Event Size (bytes)'] = data['Small Payload (bytes)'] * (1 - data['Large Event Fraction']) + data['Large Payload (bytes)'] * data['Large Event Fraction']

  data['Average Event Size (KiB)'] = data['Average Event Size (bytes)'] / 1024.0

  data = data[data['Rows Per Node'] >= data['Ring Size']].copy()

  return data

def add_aliases(data):

  data['Nodes'] = data['Node Count']
  data['Density'] = data['Event Density']
  data['Remote Event Fraction (%)'] = data['Remote Link Fraction (%)']
  return data

def clean_and_calculate(data):
  data = fill_missing_fields(data)
  
  data = topology_fields(data)
  data = time_based_fields(data)
  data = mem_based_fields(data)

  data = add_aliases(data)

  return data

def clean_failures(data):
  data = fill_missing_fields(data)
  
  data = topology_fields(data)

  data = add_aliases(data)

  return data

def brandons_theme():
  return theme(figure_size=(8,5),
            axis_title_x=element_text(size=20),
            axis_title_y=element_text(size=20),
            axis_text_x=element_text(size=16),
            axis_text_y=element_text(size=16),
            legend_title=element_text(size=20),
            legend_text=element_text(size=16),
            legend_position='bottom',
            legend_box='horizontal', 
            legend_text_position='left',
            legend_key_spacing_x=10 ) 


def read_both(success_path):
  successes = clean_and_calculate(pd.read_csv(success_path))
  failure_path = success_path.replace('.csv', '-failures.csv')
  failures = clean_failures(pd.read_csv(failure_path))
  successes['Status'] = 'Success'
  return (successes, failures)

def read_all_data(success_path):
  (successes,failures) = read_both(success_path)
  return pd.concat([successes, failures], ignore_index=True)

def read_data(success_path):
  successes = clean_and_calculate(pd.read_csv(success_path))
  successes['Status'] = 'Success'
  return successes


def orange(): 
  return '#b35806'

def purple():
  return '#542788'

def blue():
  return '#0072B2'

def red():
   return '#DC3220'


def color_to_color(c1, c2, num_points):
  start_rgb = np.array(to_rgb(c1))
  end_rgb = np.array(to_rgb(c2))
  interpolated_colors = [
    to_hex(start_rgb + (end_rgb - start_rgb) * i / (num_points - 1))
    for i in range(num_points)
  ]
  return interpolated_colors

def blue_to_red(num_points):
  return color_to_color(blue(), red(), num_points)
def blue_to_orange(num_points):
  return color_to_color(blue(), orange(), num_points)
  
def orange_purple_diverging(num_points):
  match num_points:
    case 2:
      return ['#f1a340', '#998ec3']
    case 3:
      return ['#f1a340','#f7f7f7','#998ec3']
    case 4:
      return ['#e66101', '#fdb863', '#b2abd2', '#5e3c99']
    case 5:
      return ['#e66101', '#fdb863', '#f7f7f7', '#b2abd2', '#5e3c99']
    case 6:
      return ['#b35806', '#f1a340','#fee0b6','#d8daeb','#998ec3','#542788']
    case 7:
      return ['#b35806','#f1a340','#fee0b6','#f7f7f7','#d8daeb','#998ec3','#542788']
    case 8:
      return ['#b35806','#e08214','#fdb863','#fee0b6','#d8daeb','#b2abd2','#8073ac','#542788']
    case 'continuous':
      raise ValueError(f"Unsupported number of colors: {num_points}")
