FIGURE="3235"
CLIP_COUNT=46
SPEAKER="https://www.wikidata.org/wiki/Q108723499"
TITLE="Inside the Real Narcos: Peru"
DURATION=60
NAME="fox"
EXT="mp3"

ROOT="../server/api"
TARGET="$ROOT/data/$NAME"
FIGURE_TARGET="$ROOT/figures"
mkdir -p "$FIGURE_TARGET"
mkdir -p "$TARGET"

CSV_TARGET="$FIGURE_TARGET/$FIGURE.csv"
cp "TVSM-test/labels/$FIGURE.csv" $CSV_TARGET

YAML_TARGET="$TARGET/info.yaml"
> "$YAML_TARGET"
echo $YAML_TARGET
echo "source: https://zenodo.org/records/7025971" >> "$YAML_TARGET"
echo "speaker: $SPEAKER" >> "$YAML_TARGET"
echo "license: null" >> "$YAML_TARGET"
echo "label: '$TITLE'" >> "$YAML_TARGET"
echo "clip_duration: $DURATION" >> "$YAML_TARGET"
echo "clip_count: $CLIP_COUNT" >> "$YAML_TARGET"
echo "figure: $FIGURE" >> "$YAML_TARGET"
echo "ext: $EXT" >> "$YAML_TARGET"

for i in $(seq 0 $(($CLIP_COUNT-1)));
do
  WAV_TARGET="$TARGET/$i/voice.$EXT"

  mkdir -p "$TARGET/$i"
  cp "TVSM-extractor-audio/$FIGURE-$i.$EXT" $WAV_TARGET

done
