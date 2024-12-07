const make_plain = async (root, listing) => {
  return (
    await (await fetch(`${root}/make/${listing}`)).json()
  )
}

const enrich = (transcript_state) => {
  return async (
    root, listing, transcript, old_transcript_state=[]
  ) => {
    const must_add = transcript_state.filter(
      key => !old_transcript_state.includes(key)
    );
    const parts = [
      listing, old_transcript_state.join('/'),
      must_add.join('+')
    ].filter(
      (part, index) => index !== 1 || part !== ''
    ).join('/');
    const lines = (
      await (await fetch(`${root}/enrich/${parts}`, {
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

const get_info = async (root, listing, width) => {
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
  const image = await get_image(parse, width);
  return { ...info, header, image };
}

const get_entity = async (speaker) => {
  const wiki = "https://www.wikidata.org/w/api.php";
  const root = `${wiki}?action=parse&format=json&origin=*`;
  const { parse } = (
    await (await fetch(`${root}&page=${speaker}`)).json()
  ) 
  return parse;
}

const get_image = async (parse, width) => {

  const thumb = "https://commons.wikimedia.org/w/thumb.php"
  const image_file = (parse.images || [])[0];
  return `${thumb}?width=${width}&f=${image_file}`;
}

const root = "http://localhost:7777/api";

export {
  get_info, root, get_image,
  make_plain, enrich_all,
  enrich_edits, enrich_sounds
}
