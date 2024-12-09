
Download [TVSM data](https://zenodo.org/records/7025971).

```
curl -o TVSM-test.zip "https://zenodo.org/records/7025971/files/TVSM-test.zip?download=1"
unzip TVSM-test.zip
```

Extract wav and png files

```
tvsm-extractor test 3235
bash copy_3235.sh
```

```
mkdir -p ../server/client/static/fox
```

Write the following to "../server/client/static/fox/info.yaml"

```
source: https://zenodo.org/records/7025971
speaker: https://www.wikidata.org/wiki/Q108723499
license: null
label: Inside the Real Narcos: Peru
clip_duration: 10
clip_count: 46
figure: 3235
```
