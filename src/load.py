from decode import decode_A50, decode_A50_downhill, decode_F6P, decode_tile
from sync import syncTile
from split import assignDownhillTileTracks

def load_2022_12_24(print_out=True):
    """Imports all datasets from 2022, 12, 24 at Morin Heights.
    
    Does not include Tile data, so no sync & split.
    """
    return decode_A50_downhill("../DATA/2022_12_24/Mt Morin Heights/A50/Morning ski at Morin Heights.csv", print_out=print_out, header="A50 Downhill Tracks"),\
        decode_A50("../DATA/2022_12_24/Mt Morin Heights/A50/Morning ski at Morin Heights.csv", print_out=print_out, header="A50 All Tracks"),\
        decode_F6P("../DATA/2022_12_24/Mt Morin Heights/F35/10181474438_ACTIVITY.csv", print_out=print_out, header="F6P Tracks"),\
        decode_tile("../DATA/2022_12_24/Mt Morin Heights/Tile/SENS000.CSV", print_out=print_out, header="Tile Full Recording")
    

def load_2022_12_26(
        use_alt_lpf=True,
        split_tile=True,
        print_out=True,
    ):
    """Imports all datasets from 2022, 12, 26 at Olympia.
    
    Includes the sync and split for Tile data.
    If `split_tile` is False, return a `Tile` object representing the entire logging period
    """
    a50_dh = decode_A50_downhill("../DATA/2022_12_26/Mt Olympia/A50/Morning ski at Olympia.csv", print_out=print_out, header="A50 Downhill Tracks")
    a50 = decode_A50("../DATA/2022_12_26/Mt Olympia/A50/Morning ski at Olympia.csv", print_out=print_out, header="A50 All Tracks")
    f6p = decode_F6P("../DATA/2022_12_26/Mt Olympia/F35/10190939007_ACTIVITY.csv", print_out=print_out, header="F6P Tracks")
    tile = decode_tile("../DATA/2022_12_26/Mt Olympia/Tile/SENS000.CSV", print_out=print_out, header="Tile Full Recording")
    
    tile = syncTile(
        tile=tile,
        truth=a50,
        use_lpf=use_alt_lpf,
        print_out=print_out,
        # use_mae=False,
        time_step_s=0.5,
        max_time_search_s=30,
        alt_step=0.25,
        min_alt_start=10,
        max_alt_search=50,
    )
    
    if split_tile:
        assignDownhillTileTracks(tile, a50_dh, print_out=print_out, header="Tile Split into Downhill Tracks")
    return a50_dh, a50, f6p, tile


def load_2022_12_27(
        use_alt_lpf=True,
        split_tile=True,
        print_out=True,
    ):
    """Imports all datasets from 2022, 12, 27 at Morin Heights.
    
    Includes the sync and split for Tile data.
    If `split_tile` is False, return a `Tile` object representing the entire logging period
    """
    a50_dh = decode_A50_downhill("../DATA/2022_12_27/Mt Morin Heights/A50/Morning ski at Morin Heights PATCHED.csv", print_out=print_out, header="A50 Downhill Tracks")
    a50 = decode_A50("../DATA/2022_12_27/Mt Morin Heights/A50/Morning ski at Morin Heights PATCHED.csv", print_out=print_out, header="A50 All Tracks")
    f6p = decode_F6P("../DATA/2022_12_27/Mt Morin Heights/F35/10196117595_ACTIVITY.csv", print_out=print_out, header="F6P Tracks")
    tile = decode_tile("../DATA/2022_12_27/Mt Morin Heights/Tile/SENS000.CSV", print_out=print_out, header="Tile Full Recording")
    
    tile = syncTile(
        tile=tile,
        truth=a50,
        use_lpf=use_alt_lpf,
        print_out=print_out,
        # use_mae=False,
        time_step_s=0.5,
        max_time_search_s=30,
        alt_step=0.25,
        min_alt_start=0,
        max_alt_search=20,
    )
    
    if split_tile:
        assignDownhillTileTracks(tile, a50_dh, print_out=print_out, header="Tile Split into Downhill Tracks")
    return a50_dh, a50, f6p, tile


def load_2023_12_30(
        use_alt_lpf=True,
        split_tile=True,
        print_out=True,
    ):
    """Imports all datasets from 2023, 12, 30 at Olympia.
    
    Includes the sync and split for Tile data.
    If `split_tile` is False, return a `Tile` object representing the entire logging period
    """
    a50_dh = decode_A50_downhill("../DATA/2023_12_30/Mt Olympia/A50/Mount Olympia PATCHED.csv", print_out=print_out, header="A50 Downhill Tracks")
    a50 = decode_A50("../DATA/2023_12_30/Mt Olympia/A50/Mount Olympia PATCHED.csv", print_out=print_out, header="A50 All Tracks")
    f6p = decode_F6P("../DATA/2023_12_30/Mt Olympia/F6P/13293488821_ACTIVITY.csv", print_out=print_out, header="F6P Tracks")
    tile = decode_tile("../DATA/2023_12_30/Mt Olympia/Tile/SENS000.CSV", print_out=print_out, header="Tile Full Recording")
    
    tile = syncTile(
        tile=tile,
        truth=a50,
        use_lpf=use_alt_lpf,
        print_out=print_out,
        # use_mae=False,
        time_step_s=0.5,
        max_time_search_s=30,
        alt_step=0.25,
        min_alt_start=120,
        max_alt_search=140,
    )
    
    if split_tile:
        assignDownhillTileTracks(tile, a50_dh, print_out=print_out, header="Tile Split into Downhill Tracks")
    return a50_dh, a50, f6p, tile


def load_2023_12_31(
        use_alt_lpf=True,
        split_tile=True,
        print_out=True,
    ):
    """Imports all datasets from 2023, 12, 31 at St. Sauveur.
    
    Includes the sync and split for Tile data.
    If `split_tile` is False, return a `Tile` object representing the entire logging period
    """
    a50_dh = decode_A50_downhill("../DATA/2023_12_31/Mt St Sauveur/A50/Mount St Sauveur PATCHED.csv", print_out=print_out, header="A50 Downhill Tracks")
    a50 = decode_A50("../DATA/2023_12_31/Mt St Sauveur/A50/Mount St Sauveur PATCHED.csv", print_out=print_out, header="A50 All Tracks")
    f6p = decode_F6P("../DATA/2023_12_31/Mt St Sauveur/F6P/13306856415_ACTIVITY.csv", print_out=print_out, header="F6P Tracks")
    tile = decode_tile("../DATA/2023_12_31/Mt St Sauveur/Tile/SENS000.CSV", print_out=print_out, header="Tile Full Recording")
    
    tile = syncTile(
        tile=tile,
        truth=a50,
        use_lpf=use_alt_lpf,
        print_out=print_out,
        # use_mae=False,
        time_step_s=0.5,
        max_time_search_s=5,
        alt_step=0.25,
        min_alt_start=40,
        max_alt_search=45,
    )
    
    if split_tile:
        assignDownhillTileTracks(tile, a50, print_out=print_out, header="Tile Split into Downhill Tracks")
    return a50_dh, a50, f6p, tile


def load_2024_01_01(
        use_alt_lpf=True,
        split_tile=True,
        print_out=True,
    ):
    """Imports all datasets from 2024, 1, 1 at Morin Heights.
    
    Includes the sync and split for Tile data.
    If `split_tile` is False, return a `Tile` object representing the entire logging period
    """
    a50_dh = decode_A50_downhill("../DATA/2024_01_01/Mt Morin Heights/A50/Mount Morin Heights PATCHED.csv", print_out=print_out, header="A50 Downhill Tracks")
    a50 = decode_A50("../DATA/2024_01_01/Mt Morin Heights/A50/Mount Morin Heights PATCHED.csv", print_out=print_out, header="A50 All Tracks")
    f6p = decode_F6P("../DATA/2024_01_01/Mt Morin Heights/F6P/13319383173_ACTIVITY.csv", print_out=print_out, header="F6P Tracks")
    tile = decode_tile("../DATA/2024_01_01/Mt Morin Heights/Tile/SENS000.CSV", print_out=print_out, header="Tile Full Recording")
    
    tile = syncTile(
        tile=tile,
        truth=a50,
        use_lpf=use_alt_lpf,
        print_out=print_out,
        # use_mae=False,
        time_step_s=0.5,
        max_time_search_s=30,
        alt_step=0.25,
        min_alt_start=0,
        max_alt_search=20,
    )
    
    if split_tile:
        assignDownhillTileTracks(tile, a50_dh, print_out=print_out, header="Tile Split into Downhill Tracks")
    return a50_dh, a50, f6p, tile