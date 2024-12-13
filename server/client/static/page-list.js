import StyleGlobal from "style-global" with { type: "css" };
import StylePageList from "style-page-list" with { type: "css" };
import { get_root, index_info } from "api";

class PageList extends HTMLElement {

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StylePageList
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const template = document.getElementById("page-list-view");
    const copy = template.content.cloneNode(true);
    const info_index = await(index_info(await get_root()));
    info_index.forEach(info => {
      const info_el = document.createElement("nested-list");
      info_el.setAttribute("clip_count", info.clip_count);
      info_el.setAttribute("listing", info.listing);
      info_el.setAttribute("label", info.label);
      copy.appendChild(info_el);
    });
    const button = copy.querySelector("button");
    button.addEventListener("click", () => {
      this.className = "hidden";
    });
    this.shadowRoot.appendChild(copy);
  }

  openOneListing(listing) {
    const list = this.shadowRoot.querySelectorAll("nested-list");
    [...list].forEach((list_el) => {
      list_el.setOpenDescription(
        list_el.getAttribute("listing") === listing
      )
    })
  }
};

export { PageList };
