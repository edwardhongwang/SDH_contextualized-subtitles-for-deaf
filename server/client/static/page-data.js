import StyleGlobal from "style-global" with { type: "css" };
import StylePageData from "style-page-data" with { type: "css" };
import { root, run_all, get_info, get_image } from "api";

class PageData extends HTMLElement {

  static observedAttributes = ["lines"];

  static eventHandlerKeys = [
    "srt-lines/redraw"
  ];

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StylePageData
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const listing = this.getAttribute("listing");
    const info = await get_info(
      root, listing, 100
    );
    run_all(root, listing).then((lines) => {
      this.setAttribute("lines", JSON.stringify(lines))
    });
    this.setAttribute("image", info.image);
    this.setAttribute("label", info.label);
    this.setAttribute("source", info.source);
    this.setAttribute("header", info.header);
    this.setAttribute("id", self.crypto.randomUUID());
    const template = document.getElementById("page-data-view");
    const copy = template.content.cloneNode(true);
    this.shadowRoot.appendChild(copy);
  }

  renderPaneLineList(target) {
    const lines = this.getAttribute("lines");
    const pane_el = target.querySelector("page-pane");
    if (pane_el) {
      pane_el.setAttribute("lines", lines);
    }
  }

  attributeChangedCallback(key, _, value) {
    if (key == "lines") {
      this.renderPaneLineList(this.shadowRoot);
    }
  }

  toEventHandler(key) {
    if (key === "srt-lines/redraw") {
      return ({ detail }) => {
        console.log("redraw");
        const listing = this.getAttribute("listing");
        run_all(root, listing).then((lines) => {
          this.setAttribute("lines", JSON.stringify(lines))
        });
      }
    }
  }

}

export { PageData };
