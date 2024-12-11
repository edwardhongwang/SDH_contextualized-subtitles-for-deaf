import StyleGlobal from "style-global" with { type: "css" };
import StylePagePane from "style-page-pane" with { type: "css" };

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
    const h3_el = copy.querySelector("h3");
    const h4_el = copy.querySelector("h4");
    h2_el.innerText = this.getAttribute("label");
    h3_el.innerText = this.getAttribute("clip_id");
    h4_el.innerText = this.getAttribute("header");
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
