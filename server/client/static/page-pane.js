import StyleGlobal from "style-global" with { type: "css" };
import StylePagePane from "style-page-pane" with { type: "css" };
import { get_root, get_audio_url } from "api";

class PagePane extends HTMLElement {

  static observedAttributes = [
    "lines"
  ];

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StylePagePane
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const template = document.getElementById("page-pane-view");
    const copy = template.content.cloneNode(true);
    const img_el = copy.querySelector("img");
    const h2_el = copy.querySelector("h2");
    const h4_el = copy.querySelector("h4");
    const a_el = copy.querySelector("a");
    const listing = this.getAttribute("listing");
    const clip_id = this.getAttribute("clip_id");
    h2_el.innerText = this.getAttribute("label");
    h4_el.innerText = this.getAttribute("header");
    a_el.innerText = clip_id;
    const root = await get_root();
    a_el.setAttribute(
      "href", get_audio_url(root, listing, clip_id)
    );
    a_el.setAttribute("target", "_blank");
    img_el.src = this.getAttribute("figure_src");
    this.shadowRoot.appendChild(copy);
  }

  renderLineList(target) {
    const figure_src = this.getAttribute("figure_src");
    const speaker_src = this.getAttribute("speaker_src");
    const lines = this.getAttribute("lines");
    const line_list_el = target.querySelector("line-list");
    const img_el = this.shadowRoot.querySelector("img");
    if (img_el && figure_src) {
      img_el.src = figure_src;
    }
    if (line_list_el) {
      line_list_el.setAttribute("speaker_src", speaker_src);
      line_list_el.setAttribute("lines", lines);
    }
  }

  attributeChangedCallback(key, _, value) {
    if (key == "lines") {
      this.renderLineList(this.shadowRoot);
    }
  }
}

export { PagePane };
