import ee, geemap,datetime
import geopandas as gpd
import pandas as pd

ee.Initialize()



def S2masking(image): 
        cloudProb = image.select('MSK_CLDPRB')  # покрытие облаками
        snowProb = image.select('MSK_SNWPRB') # покрытие снегом
        cloud = cloudProb.lt(1) # создали бинарную маску иными словами просто все что имеет значение меньше 5 одна группа выше другая
                            # а мы помним что пиксели принимают значения от 0 до 255
        snow = snowProb.lt(1) # тоже самое что с облаками
        scl = image.select('SCL') # слой с классификатором(есть в sentinel 2 уровня обработки 2А)
        shadow = scl.neq(3);# 3 в классификации это тени от облаков
        cirrus_medium = scl.neq(8) # тоже по классификации облака 
        cirrus_high = scl.neq(9) # аналогично облака
        cirrus = scl.neq(10); # 10 это перистые облака или цирусы
        return  image.updateMask(cirrus).updateMask(cirrus_medium).updateMask(cirrus_high)

def downloader(image, boundary, description = 'sentinel_2',google_folder = 'raster_data',  scale = 10):
    geemap.ee_export_image_to_drive(
        image,
        description = description,
        folder = google_folder,
        region = boundary,
        scale = scale
    )


class SEN2_downloader:
    def __init__(self,  year : str, region_boundary):
        """
        input:
        year - год str 
        region_boundary - граница региона в gpd

        """
        self.boundary = geemap.geopandas_to_ee(region_boundary)
        self.year = year

    def get_collection(self ,cloud_cover = 10):
        self.row_image = ee.ImageCollection('COPERNICUS/S2_SR') \
                    .filterDate('2022-05-01', '2022-10-01') \
                    .filterBounds(self.boundary) \
                    .filterMetadata("CLOUD_COVERAGE_ASSESSMENT", 'less_than', cloud_cover) \
                    .map(S2masking) 
        return self.row_image

    def get_rgb_nir(self):
        self.rgb_nir = self.row_image.select(['B4','B3','B2', 'B8']) \
                    .median().clip(self.boundary)
        downloader(self.rgb_nir, self.boundary, description = f'Sentinel2_RGB_NIR_{self.year}.tif')

