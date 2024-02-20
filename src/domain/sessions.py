from constants.offsets import offsets_2022_12_26, offsets_2022_12_27, offsets_2023_12_30, offsets_2023_12_31, offsets_2024_01_01
from domain.session_logger import SessionLogger as logger
from models.session import Session

class Session_2022_12_26(Session):
    """Imports session from 2022, 12, 26 at Olympia."""
    def __init__(self, offsets=None) -> None:
        logger.info('Importing Session from 2022, 12, 26 at Olympia.')
        super().__init__(
            tile_file="../DATA/2022_12_26/Mt Olympia/Tile/SENS000.CSV",
            a50_file="../DATA/2022_12_26/Mt Olympia/A50/Morning ski at Olympia.csv",
            f6p_file="../DATA/2022_12_26/Mt Olympia/F35/10190939007_ACTIVITY.csv",
            offsets=offsets_2022_12_26() if offsets is None else offsets,
        )


class Session_2022_12_27(Session):
    """Imports session from 2022, 12, 27 at Morin Heights."""
    def __init__(self, offsets=None) -> None:
        logger.info('Importing Session from 2022, 12, 27 at Morin Heights.')
        super().__init__(
            tile_file="../DATA/2022_12_27/Mt Morin Heights/Tile/SENS000.CSV",
            a50_file="../DATA/2022_12_27/Mt Morin Heights/A50/Morning ski at Morin Heights PATCHED.csv",
            f6p_file="../DATA/2022_12_27/Mt Morin Heights/F35/10196117595_ACTIVITY.csv",
            offsets=offsets_2022_12_27() if offsets is None else offsets,
        )


class Session_2023_12_30(Session):
    """Imports session from 2023, 12, 30 at Olympia."""
    def __init__(self, offsets=None) -> None:
        logger.info('Importing Session from 2023, 12, 30 at Olympia.')
        super().__init__(
            tile_file="../DATA/2023_12_30/Mt Olympia/Tile/SENS000.CSV",
            a50_file="../DATA/2023_12_30/Mt Olympia/A50/Mount Olympia PATCHED.csv",
            f6p_file="../DATA/2023_12_30/Mt Olympia/F6P/13293488821_ACTIVITY.csv",
            offsets=offsets_2023_12_30() if offsets is None else offsets,
        )


class Session_2023_12_31(Session):
    """Imports session from 2023, 12, 31 at St. Sauveur."""
    def __init__(self, offsets=None) -> None:
        logger.info('Importing Session from 2023, 12, 31 at St. Sauveur.')
        super().__init__(
            tile_file="../DATA/2023_12_31/Mt St Sauveur/Tile/SENS000.CSV",
            a50_file="../DATA/2023_12_31/Mt St Sauveur/A50/Mount St Sauveur PATCHED.csv",
            f6p_file="../DATA/2023_12_31/Mt St Sauveur/F6P/13306856415_ACTIVITY.csv",
            offsets=offsets_2023_12_31() if offsets is None else offsets,
        )


class Session_2024_01_01(Session):
    """Imports session from 2024, 1, 1 at Morin Heights."""
    def __init__(self, offsets=None) -> None:
        logger.info('Importing Session from 2024, 1, 1 at Morin Heights.')
        super().__init__(
            tile_file="../DATA/2024_01_01/Mt Morin Heights/Tile/SENS000.CSV",
            a50_file="../DATA/2024_01_01/Mt Morin Heights/A50/Mount Morin Heights PATCHED.csv",
            f6p_file="../DATA/2024_01_01/Mt Morin Heights/F6P/13319383173_ACTIVITY.csv",
            offsets=offsets_2024_01_01() if offsets is None else offsets,
        )


class Session_2024_02_08(Session):
    """Imports session from 2024, 2, 8 for testing orientation axes."""
    def __init__(self, offsets=None) -> None:
        logger.info('Importing Session from 2024, 2, 8 for testing orientation axes.')
        super().__init__(
            tile_file="../DATA/2024_02_08/Tile/SENS000.CSV",
        )


class Session_2024_02_09(Session):
    """Imports session from 2024, 2, 9 for testing orientation axes."""
    def __init__(self, offsets=None) -> None:
        logger.info('Importing Session from 2024, 2, 9 for testing orientation axes.')
        super().__init__(
            tile_file="../DATA/2024_02_09/Tile-frame/SENS000.CSV",
        )


class Session_2024_02_09_Boot_Frame(Session):
    """Imports session from 2024, 2, 9 for testing orientation axes, done in the boot frame."""
    def __init__(self, offsets=None) -> None:
        logger.info('Importing Session from 2024, 2, 9 for testing orientation axes, done in the boot frame.')
        super().__init__(
            tile_file="../DATA/2024_02_09/Boot-frame/SENS000.CSV",
        )
