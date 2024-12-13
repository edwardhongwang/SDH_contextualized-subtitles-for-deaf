const make_plain = async (root, listing, clip_id) => {
  const listing_path = get_listing_path(
    listing, clip_id, [], []
  );
  return (
    await (
      await fetch(
        `${root}/make/${listing_path}`
      )
    ).json()
  )
}

const enrich = (transcript_state) => {
  return async (
    root, listing, clip_id, transcript, old_transcript_state=[]
  ) => {
    const must_add = transcript_state.filter(
      key => !old_transcript_state.includes(key)
    );
    const listing_path = get_listing_path(
      listing, clip_id, old_transcript_state, must_add
    );
    const lines = (
      await (await fetch(`${root}/enrich/${listing_path}`, {
        method: "POST", body: JSON.stringify(transcript),
        headers: {
          "Content-Type": "application/json",
        }
      })).json()
    )
    return {
      lines, transcript_state
    }
  }
}

const enrich_all = enrich([
  "edits", "sounds", "emotions"
]);
const enrich_edits = enrich([ "edits" ]);
const enrich_sounds = enrich([ "sounds" ]);

const index_info = async (root) => {
  const info_index = (
    await (await fetch(`${root}/index/info`)).json()
  )
  return info_index.map(info => {
    const { listing, label, clip_count } = info;
    return { listing, label, clip_count };
  })
}

const get_info = async (
  root, listing, clip_id, transcript_state, width
) => {
  const info = (
    await (await fetch(`${root}/info/${listing}`)).json()
  )
  const parse = await get_entity(info.speaker.split('/').pop());
  const { displaytitle } = parse;
  const title_el = document.createElement('html')
  title_el.innerHTML = displaytitle;
  const header = (
    title_el.querySelector('.wikibase-title-label')
  ).innerText;
  const figure_src = await get_figure_image(
    root, listing, clip_id, transcript_state
  );
  const speaker_src = (
    await get_thumb_image(parse, width)
  );
  return { 
    ...info, header, images : {
      figure_src, speaker_src
    } 
  };
}

const get_entity = async (speaker) => {
  const wiki = "https://www.wikidata.org/w/api.php";
  const root = `${wiki}?action=parse&format=json&origin=*`;
  const { parse } = (
    await (await fetch(`${root}&page=${speaker}`)).json()
  ) 
  return parse;
}

const get_thumb_image = async (parse, width) => {

  const thumb = "https://commons.wikimedia.org/w/thumb.php"
  const image_file = (parse.images || [])[0];
  if (!image_file) {
    return "./static/no-speaker.png";
  }
  return `${thumb}?width=${width}&f=${image_file}`;
}

const get_figure_image = async (
  root, listing, clip_id, transcript_state=[]
) => {
  const listing_path = get_listing_path(
    listing, clip_id, transcript_state, []
  );
  return `${root}/figure/${listing_path}/figure.png`;
}

const get_listing_path = (
  listing, clip_id, transcript_state, must_add
) => {
  return [
    listing, clip_id, transcript_state.join('/'),
    must_add.join('+')
  ].filter(
    (part, index) => part !== ''
  ).join('/');
}

const get_audio_url = (
  root, listing, clip_id
) => {
  return `${root}/audio/${listing}/${clip_id}/voice.mp3`;
}

const root = "http://localhost:7777/api";

export {
  get_info, index_info, root,
  make_plain, enrich_all,
  enrich_edits, enrich_sounds,
  get_audio_url
}
