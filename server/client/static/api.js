const run_all = async (root, listing) => {
  return (
    await (await fetch(`${root}/sdh/all/${listing}`)).json()
  )
}

const get_info = async (root, listing, width) => {
  const info = (
    await (await fetch(`${root}/sdh/info/${listing}`)).json()
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
  get_info, run_all, root, get_image
}
