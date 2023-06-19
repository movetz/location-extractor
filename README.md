# location-extractor

```python
from location_extractor.location import CsvCollection
from location_extractor.pipelines.ru_pipeline import RuPipeline

text = """
В поселке Глушково в Курской области ВСУ сбросили взрывное устройство на физкультурно-оздоровительный комплекс, 
предварительно пострадали два человека — губернатор
"""

collection = CsvCollection(
    locations_path=f"location_extractor/files/locations.csv",
    regions_path=f"location_extractor/files/regions.csv",
)

pipeline = RuPipeline(locations=collection)

regions, locations = pipeline.extract_locations_from_text(text)

for region in regions:
    print(f"{region.name_ru}")

print("============================")

for location in locations:
    print(f"{location.name_ru} {location.region.name_ru} {location.lat}:{location.lon}")

# Example output:

# Курская область
# ============================
# Глушково Полтавская область 49.43436:33.68082
# Глушково Курская область 51.33300:34.63300
# Глушково Курская область 51.70000:35.5830
```