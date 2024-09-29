from opentrons import protocol_api
import datetime

metadata = {
    'protocolName': 'BIEN 267 Plasmid Ligation',
    "author": "TUES PM Group 4",
    'description':
    '''
      1) Takes a DNA concentration input and calculates appropriate volumes for gene insert and vector DNA to be combined
          ... in 3:1 ratio for 20 uL final volume
      2) perform a control reaction with only the digested vector and ligase
      3) perform a ligation reaction on ice, with gentle mixture of reaction using up and down pipetting
      4) add if/else for catching tests
    '''
}

requirements = {"robotType": "OT-2", "apiLevel": "2.19"}

def add_parameters(parameters: protocol_api.Parameters):

  parameters.add_float(

    variable_name = "eppendorf_depth",

    display_name = "Eppendorf Depth",

    description = "Depth  at which  pipettes  will  access  Eppendorf  tube",

    default = 36.5,

    minimum = 1.0,

    maximum = 40.0,

    unit = "mm"

  )

  parameters.add_int(

    variable_name = "t_incubate",

    display_name = "Incubation Time",

    description = "Time for the sample to incubate for ligation",

    default = 15,

    minimum = 15,

    maximum = 20,

    unit = "minutes"

  )

  parameters.add_bool (

    variable_name = "test_run",

    display_name = "Test  Run",

    description = "",

    default = False

  )

def initialize(protocol: protocol_api.ProtocolContext):

  # Get the depth of the eppendorf tubes from run_time parameters
  eppendorf_depth = protocol.params.eppendorf_depth

  """
  Location map for loab_labware args: 1 = temp, 3 = iced reagents, 5 = reagents & tubes, 8 = p20, 9 = p300
  """

  ### Defining pipette tip addresses ###
  # 300 uL tips
  global p300
  p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[protocol.load_labware('opentrons_96_tiprack_300ul', '9')])
  # 20 uL tips
  global p20
  p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[protocol.load_labware('opentrons_96_tiprack_20ul', '8')])

  ### Defining temperature module addresses ###
  # Load the temperature module with the aluminum tube holder
  global temp_mod
  temp_mod = protocol.load_module('temperature  module  gen2','1')
  global temp_tubes
  temp_tubes = temp_mod.load_labware('opentrons_24_aluminumblock_nest_1 .5ml_snapcap', '1')
  # Load a tube rack
  global tube_rack
  tube_rack = protocol.load_labware('opentrons_24_tuberack_nest_1 .5ml_snapcap ', '5')
  # Load a temperature controlled "chilled" tube rack
  global chilled_rack
  chilled_rack = protocol.load_labware('opentrons_24_tuberack_nest_1 .5ml_snapcap ', '3')

  ### Defining sample addresses ###
  # Address for Vector Eppendorf Tube
  global vector
  vector = tube_rack.wells_by_name()['D1'].top(-eppendorf_depth) # double-digested pESC-H (cut with BamHI-HF and SalI-HF)
  # Address for Insert Eppendorf Tube (Uncut)
  global insert_uncut
  insert_uncut = tube_rack.wells_by_name()['D2'].top(-eppendorf_depth) # gene fragment of undigested pTOPO-LimS-L plasmid
  # Address for Insert Eppendorf Tube (Second Cut)
  global insert_double_cut
  insert_double_cut = tube_rack.wells_by_name()['D3'].top(-eppendorf_depth) # gene fragment of double digested pTOPO-LimS-L plasmid (cut with BamHI-HF and SalI-HF)
  # Address for Eppendorf Tube Containing Water
  global water
  water = tube_rack.wells_by_name()['D4'].top(-eppendorf_depth) # nuclease free water
  # Addresses for the Result Eppendorf Tube
  global result_top
  global result_bottom
  result_top = temp_tubes.wells_by_name()['A8'].top() # final result tube, simply for putting in samples
  result_bottom = temp_tubes.wells_by_name()['A8'].top(-eppendorf_depth) # final result tube, but tip goes all the way (for mixing)
  # Addresses for the control tubes
  global control_1_top
  global control_1_bottom
  control_1_top = temp_tubes.wells_by_name()['B8'].top() # location for control 1
  control_1_bottom = temp_tubes.wells_by_name()['B8'].top(-eppendorf_depth) # for mixing
  global control_2_top
  global control_2_bottom
  control_2_top = temp_tubes.wells_by_name()['C8'].top() # location for control 2
  control_2_bottom = temp_tubes.wells_by_name()['C8'].top(-eppendorf_depth) # for mixing
  # Address for the Buffer Tube
  global buffer
  buffer = chilled_rack.wells_by_name()['A1'].top(-eppendorf_depth) # T4 DNA ligase buffer (10X)
  # Adress for the Ligase Tuve
  global ligase
  ligase = chilled_rack.wells_by_name()['B1'].top(-eppendorf_depth) # T4 DNA ligase

def run(protocol: protocol_api.ProtocolContext, c_vector_tube, c_insert_double_tube, c_insert_uncut_tube, v_final, c_vector_final, c_insert_final):
  """
  c_vector_tube: DNA concentration within the vector sample Eppendorf tube (in ng/uL)
  c_insert_double_tube: DNA concentration within the double-cut insert sample Eppendorf tube (in ng/uL)
  c_insert_uncut_tube: DNA concentration within the uncut insert sample Eppendorf tube (in ng/uL)
  v_final: DNA concentration within the vector sample Eppendorf tube (in uL)
  c_vector_final: Desired DNA concentration of insert DNA in final reaction tube  (in ng/uL)
  c_insert_final: Desired DNA concentration of vector DNA in final reaction tube (in ng/uL)
  """
  # Print to acknowledge start of run
  start = datetime.datetime.now()
  print('Run commencing at:', start, ".")

  add_parameters()

  initialize()

  temp_mod.set_temperature(22)

  assert 3*c_vector_final == c_insert_final

  ### Reaction Tube Addresses ###
  # All reaction tubes (top of the tube so pipette doesn't need to go in)
  well_locations_top = [result_top, control_1_top, control_2_top]
  # All reaction tubes (bottom of the tube to mix so PIPETTE MUST BE DISCARDED after every use)
  well_locations_bottom = [result_bottom, control_1_bottom, control_2_bottom]

  """ QUESTION: WHAT SHOULD BE FINAL CONCENTRATION? """
  ### Dilution Calculations ###
  # Volume from insert (uncut) tube needed to be picked up (round to nearest integer)
  v_insert_tube_uncut = round(c_insert_final*v_final/c_insert_uncut_tube)
  print("Volume of uncut insert DNA added to control2:", v_insert_tube_uncut, "uL.")
  # Volume from insert (double cut) tube needed to be picked up (round to nearest integer)
  v_insert_tube_double_cut = round(c_insert_final*v_final/c_insert_double_tube)
  print("Volume of double cut insert DNA added to result:", v_insert_tube_double_cut, "uL.")
  # Volume from vector tube needed to be picked up (round to nearest integer)
  v_vector_tube = round(c_vector_final*v_final/c_vector_tube)
  print("Volume of vector DNA added to all reaction tubes:", v_vector_tube, "uL.")

  ### Reaction Volumes ###
  # Volume of ligation buffer added to each reaction tube (in uL)
  ligase_buffer_volume = 2
  # Volume of ligase added to each reaction tube (in uL)
  ligase_volume = 1

  ### Add Nuclease-Free Water ###
  # Nuclease-free water to add to each tube
  water_added_uncut = v_final - ligase_buffer_volume - ligase_volume - v_vector_tube - v_insert_tube_uncut
  water_added_double_cut = v_final - ligase_buffer_volume - ligase_volume - v_vector_tube - v_insert_tube_double_cut
  water_added = v_final - ligase_buffer_volume - ligase_volume - v_vector_tube
  assert water_to_be_added <= 300
  # Pick up p300 tip
  p300.pick_up_tip()
  # Add the water needed for result tube (double cut insert DNA)
  p300.transfer(water_added_double_cut, ligase, result, new_tip="never")
  # Add the water needed for control1 tube (no insert DNA)
  p300.transfer(water_added, ligase, control_1_top, new_tip="never")
  # Add the water needed for control2 tube (single cut insert DNA)
  p300.transfer(water_added_uncut, ligase, control_2_top, new_tip="never")
  # Get rid of tip
  p300.drop_tip()

  ### Add Double-Cut Insert DNA to Result ###
  assert v_insert_tube_double_cut <= 20
  # Use p20 tip
  p20.pick_up_tip()
  p20.aspirate(v_insert_double_tube, insert_double_cut)
  # Add double cut insert to result tube
  p20.dispense(v_insert_double_tube, result_top)
  # Drop tip
  p20.drop_tip()

  ### Add Uncut Insert DNA to Control 2 ###
  assert v_insert_tube_uncut <= 20
  # Use p20 tip
  p20.pick_up_tip()
  p20.aspirate(v_insert_tube_uncut, insert_uncut)
  # Add uncut insert to control 2 tube
  p20.dispense(v_insert_tube_uncut, control_2_top)
  # Drop tip
  p20.drop_tip()

  ### Add Vector DNA to Tubes ###
  assert v_vector <= 20
  # Use p20 tip
  p20.pick_up_tip()
  # Pick up 3 times as much volume for each tube
  p20.aspirate(len(well_locations_top)*v_vector_tube, vector)
  # Add vector DNA to each tube (top, so don't need to dispense after every tube)
  for well in well_locations_top:
    p20.dispense(v_insert_tube, well)
   # Drop tip
  p20.drop_tip()

  ### Add Ligase Buffer to Tubes ###
  assert ligase_buffer_volume <= 20
  # Use p20 tip
  p20.pick_up_tip()
  # Pick up 6 uL to put 2 uL in each tube
  p20.aspirate(len(well_locations_top)*ligase_buffer_volume, buffer)
  # Add 2 uL ligase buffer to each tube (top, so don't need to dispense after every tube)
  for well in well_locations_top:
    p20.dispense(ligase_buffer_volume, well)
   # Drop tip
  p20.drop_tip()

  ### Add Ligase to Tubes ###
  assert ligase_volume <= 20
  # For each tube, add ligase (bottom, must pick and dispense tip after every tube)
  p20.pick_up_tip()
  for well in well_locations_bottom:
    # Pick up ligase, drop it into well, mix
    """ QUESTION: HOW MANY TIMES SHOULD WE MIX? """
    p20.transfer(ligase_volume, ligase, well, mix_after =(3, v_final*3/4), new_tip="always")

  now = datetime.datetime.now()

  incubation_time = protocol.params.t_incubate
  print("Ligase added to tubes at:", now, ". The incubation will be complete at:", now + datetime.timedelta(minutes=incubation_time),".")

  protocol.delay(minutes = incubation_time)

  """ QUESTION: WHAT TEMPERATURE SHOULD THIS BE AT? """
  # Sets the temperature of the module to 0 degrees C
  temp_mod.set_temperature(0)

  # Print to acknowledge end of run
  end = datetime.datetime.now()
  print('Run finished at: ', end, ".")

###### ON THE DAY OF THE EXPERIMENT ######
# Run the protocal with DNA concentration of our samples (enter the values the day of)
#run(c_vector_tube, c_insert_double_tube, c_insert_uncut_tube, v_final, c_vector_final, c_insert_final)
