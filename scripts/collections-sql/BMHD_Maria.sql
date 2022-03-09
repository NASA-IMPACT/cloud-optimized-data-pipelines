INSERT INTO pgstac.collections (content) VALUES('{
    "id": "BMHD_Maria",
   "type": "Collection",
   "links":[
   ],
   "title":"BMHD_Maria",
   "extent":{
      "spatial":{
         "bbox":[
            [
              -67.27167653359618,
              17.912138994450856,
              -65.57478762584185,
              18.51569455671654
            ]
         ]
      },
      "temporal":{
         "interval":[
            [
               "2017-07-21T00:00:00Z",
               "2018-03-20T00:00:00Z"
            ]
         ]
      }
   },
   "license":"public-domain",
   "description":"BMHDMaria",
   "stac_version":"1.0.0"
}')
ON CONFLICT (id) DO UPDATE 
  SET content = excluded.content;
