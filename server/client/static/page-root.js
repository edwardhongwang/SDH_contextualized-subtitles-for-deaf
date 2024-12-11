import StyleGlobal from "style-global" with { type: "css" };
import StylePageRoot from "style-page-root" with { type: "css" };

class PageRoot extends HTMLElement {

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StylePageRoot
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const template = document.getElementById("page-root-view");
    this.shadowRoot.appendChild(template.content.cloneNode(true));
  }

  createNewPage(listing, clip_id) {
    const new_page_data = document.createElement("page-data");
    new_page_data.setAttribute("transcript_state", "");
    new_page_data.setAttribute("lines", "[]");
    new_page_data.setAttribute("listing", listing);
    new_page_data.setAttribute("clip_id", clip_id);
    this.shadowRoot.prepend(new_page_data);
    window.scrollTo(0, 0);
  }

}

export { PageRoot };
