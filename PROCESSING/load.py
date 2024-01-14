from decode import decode_A50, decode_A50_downhill, decode_F6P, decode_tile

def load_2022_12_24():
    return decode_A50_downhill("../DATA/2022_12_24/Mt Morin Heights/A50/Morning ski at Morin Heights.csv"),\
        decode_A50("../DATA/2022_12_24/Mt Morin Heights/A50/Morning ski at Morin Heights.csv"),\
        decode_F6P("../DATA/2022_12_24/Mt Morin Heights/F35/10181474438_ACTIVITY.csv"),\
        decode_tile("../DATA/2022_12_24/Mt Morin Heights/Tile/SENS000.CSV")
    

def load_2022_12_26():
    return decode_A50_downhill("../DATA/2022_12_26/Mt Olympia/A50/Morning ski at Olympia.csv"),\
        decode_A50("../DATA/2022_12_26/Mt Olympia/A50/Morning ski at Olympia.csv"), \
        decode_F6P("../DATA/2022_12_26/Mt Olympia/F35/10190939007_ACTIVITY.csv"), \
        decode_tile("../DATA/2022_12_26/Mt Olympia/Tile/SENS000.CSV")

def load_2022_12_27():
    return decode_A50_downhill("../DATA/2022_12_27/Mt Morin Heights/A50/Morning ski at Morin Heights PATCHED.csv"),\
        decode_A50("../DATA/2022_12_27/Mt Morin Heights/A50/Morning ski at Morin Heights PATCHED.csv"),\
        decode_F6P("../DATA/2022_12_27/Mt Morin Heights/F35/10196117595_ACTIVITY.csv"),\
        decode_tile("../DATA/2022_12_27/Mt Morin Heights/Tile/SENS000.CSV")

def load_2023_12_30():
    return decode_A50_downhill("../DATA/2023_12_30/Mt Olympia/A50/Mount Olympia PATCHED.csv"),\
        decode_A50("../DATA/2023_12_30/Mt Olympia/A50/Mount Olympia PATCHED.csv"),\
        decode_F6P("../DATA/2023_12_30/Mt Olympia/F6P/13293488821_ACTIVITY.csv"),\
        decode_tile("../DATA/2023_12_30/Mt Olympia/Tile/SENS000.CSV")

def load_2023_12_31():
    return decode_A50_downhill("../DATA/2023_12_31/Mt St Sauveur/A50/Mount St Sauveur PATCHED.csv"),\
        decode_A50("../DATA/2023_12_31/Mt St Sauveur/A50/Mount St Sauveur PATCHED.csv"),\
        decode_F6P("../DATA/2023_12_31/Mt St Sauveur/F6P/13306856415_ACTIVITY.csv"),\
        decode_tile("../DATA/2023_12_31/Mt St Sauveur/Tile/SENS000.CSV")

def load_2024_01_01():
    return decode_A50_downhill("../DATA/2024_01_01/Mt Morin Heights/A50/Mount Morin Heights PATCHED.csv"),\
        decode_A50("../DATA/2024_01_01/Mt Morin Heights/A50/Mount Morin Heights PATCHED.csv"),\
        decode_F6P("../DATA/2024_01_01/Mt Morin Heights/F6P/13319383173_ACTIVITY.csv"),\
        decode_tile("../DATA/2024_01_01/Mt Morin Heights/Tile/SENS000.CSV")