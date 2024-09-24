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
                   ''',
    'apiLevel': '2.19'
}

# Runtime parameters can be added here for DNA content of each sample

def run(protocol: protocol_api.ProtocolContext):
            ### LOCATION MAP: 1=temp, 3=iced reagents, 4=other reagents 5=tubes, 8=p20, 9=p300
            ### Temperature module must be located on the LEFT side & the ice bath consumes the two spaces next to it, preventing adjacency
     # Load pipettes
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[protocol.load_labware('opentrons_96_tiprack_300ul', '9')])
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[protocol.load_labware('opentrons_96_tiprack_20ul', '8')])
    # Access your runtime parameters if you added any
    
    # Load the temperature module with the aluminum tube holder
    temp_mod = protocol.load_module('temperature  module  gen2','1') ### What goes in the aluminum tube holder? Referred to as temp_tubes
    temp_tubes = temp_mod.load_labware('opentrons_24_aluminumblock_nest_1 .5ml_snapcap', '1')
    # Load a tube rack
    tube_rack = protocol.load_labware('opentrons_24_tuberack_nest_1 .5ml_snapcap ', '4')
    # Define your reagent locations and empty tubes
            ### define a location for 1) digested and purified pESC-H vector, 2) digested and purified gene insert, 3) nuclease free water, 4) empty tubes
    # Calculate the amounts to add based on the DNA content
            ### request input of DNA concentration in pESC-H vector and of DNA concentration in LimS-L insert
            ### use that input to calculate amounts to add of vector and insert to maintain a 3:1 vector insert concentration ratio
            ### what do we dilute this with to achieve the target ratios?
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
