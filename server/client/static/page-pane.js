import StyleGlobal from "style-global" with { type: "css" };
import StylePagePane from "style-page-pane" with { type: "css" };

class PagePane extends HTMLElement {

  static observedAttributes = [
    "lines"
];
  static eventHandlerKeys = [
    "srt-lines/redraw"
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
    const h3_el = copy.querySelector("h3");
    const h4_el = copy.querySelector("h4");
    h3_el.innerText = this.getAttribute("label");
    h4_el.innerText = this.getAttribute("header");
    img_el.src = this.getAttribute("image");
    this.shadowRoot.appendChild(copy);
  }

  renderLineList(target) {
    const lines = this.getAttribute("lines");
    const line_list_el = target.querySelector("line-list");
    if (line_list_el) {
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
