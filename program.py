from opentrons import protocol_api

metadata = {
    'protocolName': 'BIEN 267 Plasmid Ligation',
    "author": "TUES PM Group 4",
    'description': '''
                      1) Takes a DNA concentration input and calculates appropriate volumes for gene insert and vector DNA to be combined 
                         ... in 3:1 ratio for 20 uL final volume
                      2) perform a control reaction with only the digested vector and ligase
                      3) perform a ligation reaction on ice, with gentle mixture of reaction using up and down pipetting
                      4) add if/else for catching tests
                   '''
}

requirements = {"robotType": "OT-2", "apiLevel": "2.19"}


# Runtime parameters can be added here for DNA content of each sample

def run(protocol: protocol_api.ProtocolContext):
            # LOCATION MAP: 1=temp, 3=iced reagents, 5=reagents & tubes, 8=p20, 9=p300
            # Temperature module must be located on the LEFT side & the ice bath consumes the two spaces next to it, preventing adjacency
     # Load pipettes
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[protocol.load_labware('opentrons_96_tiprack_300ul', '9')])
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[protocol.load_labware('opentrons_96_tiprack_20ul', '8')])
    # Access your runtime parameters if you added any

    # Load the temperature module with the aluminum tube holder
    temp_mod = protocol.load_module('temperature  module  gen2','1') ### What items are supposed to go in the aluminum tubes holder?
    temp_tubes = temp_mod.load_labware('opentrons_24_aluminumblock_nest_1 .5ml_snapcap', '1')
    # Load a tube rack
    tube_rack = protocol.load_labware('opentrons_24_tuberack_nest_1 .5ml_snapcap ', '5')
        # Load a temperature controlled "chilled" tube rack
        # This will contain the DNA ligase & buffer, as they are supposed to be on ice. However, this doesn't seem to require a temp mod - the lab uses modified labware.
    chilled_rack = protocol.load_labware('opentrons_24_tuberack_nest_1 .5ml_snapcap ', '3')
    # Define your reagent locations and empty tubes
    vector = tube_rack.wells_by_name()['B1'].top(-eppendorf_depth) # double-digested pESC-H (cut with BamHI-HF and SalI-HF)
    insert = tube_rack.wells_by_name()['B2'].top(-eppendorf_depth) # gene fragment of double digested pTOPO-LimS-L plasmid (cut with BamHI-HF and SalI-HF)
    water = tube_rack.wells_by_name()['B3'].top(-eppendorf_depth) # nuclease free water
    result = tube_rack.wells_by_name()['A1'].top(-eppendorf_depth) # location for final, outputted result of ligation
    buffer = chilled_rack.wells_by_name()['D8'].top(-eppendorf_depth) # T4 DNA ligase buffer (10X)
    ligase = chilled_rack.wells_by_name()['C8'].top(-eppendorf_depth) # T4 DNA ligase
        # Questions
            # 1. What is the purpose of the temp_mod's temp_tubes? What is being stored there? What temp is required?
            # 2. If the temp_mod is being used for temp_tubes, how are we supposed to chill the result at 4 degrees prior to transformation? The chilled rack?
            # 3. 
    # Calculate the amounts to add based on the DNA content
    c_vector = float(input("Concentration of Vector (ng/uL): "))
    c_insert = float(input("Concentration of Insert (ng/uL): "))
        # can reduce concentration, but not increase concentration
    if 3*c_insert > c_vector:
        c2_insert = (1/3)*c_vector
        v_insert = float(input("Volume of Insert (uL): "))
        v2_insert = (c_insert/c2_insert)*v_insert
        water_add = v2_insert - v_insert
    elif 3*c_insert < c_vector:
        c2_vector = 3*c_insert
        v_vector = float(input("Volume of Vector (uL): "))
        v2_vector = (c_vector/c2_vector)*v_vector
        water_add = v2_vector - v_vector
        # calculate amount of water to add using target concentration for the specific sample and the known concentration
        # Probably best to include the physical actions to add the water here within the if/elif, as water_add is defined within the conditions themselves.
    # Add the right amounts of each reagent and digest
            ### Factors to consider in each step: Original location, Final location, Volume. Tip disposal is apparently automated, although we'll need to confirm this. 
            ### Add 2 uL of T4 DNA Ligase Buffer (10X), requires thawing and resuspension at room temperature before use
            ### Add volume of Vector DNA determined in last step
            ### Add volume of Insert DNA determined in last step
            ### Add nuclease free water to reach total of 20 uL (calculated based on volumes of vector DNA and insert DNA)
                ### V = 20 - (2 + vDNA + iDNA)
            ### Add 1 uL of T4 DNA Ligase
    # Incubate at room temperature for 30 minutes
            ### Potentially requires temperature control adjustment. 
    # Chill at 4 degrees prior to the transformation
            ### Potentially requires temperature control adjustment. 
