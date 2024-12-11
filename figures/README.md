
Download [TVSM data](https://zenodo.org/records/7025971).

```
curl -o TVSM-test.zip "https://zenodo.org/records/7025971/files/TVSM-test.zip?download=1"
unzip TVSM-test.zip
```

Extract wav and png files

```
tvsm-extractor test 3233 3235
bash copy_3233.sh
bash copy_3235.sh
```
