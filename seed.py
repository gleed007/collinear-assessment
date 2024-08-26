from huggingface_hub import list_datasets

from core.database import SessionLocal
from dataset.models import DatasetInfo, Impact


def seed_datasets():
  with SessionLocal() as db:
    table_data=db.query(DatasetInfo).first()
    if table_data is None:
      public_datasets = list_datasets()
      for ds in list(public_datasets)[:100]:
        data = {
          "name": ds.id,
          "author": ds.author,
          "created_at": ds.created_at,
          "last_modified": ds.last_modified,
          "downloads": ds.downloads,
          "likes": ds.likes,
        }
        sz = list(filter(lambda x: x.split(":")[0] == "size_categories", ds.tags))
        if len(sz) == 0:
          cat = Impact.LOW
        else:
          cat = sz[0].split(":")[1]
          if cat == "n<1K" or cat == "1K<n<10K" or cat == "10K<n<100K" or cat == "100K<n<1M":
            impact = Impact.LOW
          elif cat == "1M<n<10M" or cat == "10M<n<100M":
            impact = Impact.MEDIUM
          else:
            impact = Impact.HIGH

        data["size_category"] = cat
        data["impact"] = impact
        try:
          ds_info = DatasetInfo(**data)
          db.add(ds_info)
          db.commit()
        except Exception as e:
          db.rollback()
          print(e)