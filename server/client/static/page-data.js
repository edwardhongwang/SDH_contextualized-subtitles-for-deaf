import StyleGlobal from "style-global" with { type: "css" };
import StylePageData from "style-page-data" with { type: "css" };
import { root, get_info, get_image } from "api";
import { make_plain, enrich_all } from "api";

class PageData extends HTMLElement {

  static observedAttributes = ["lines"];

  static eventHandlerKeys = [
    "srt-page/enrich"
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
    make_plain(root, listing).then((lines) => {
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
    const transcript_state = this.getAttribute(
      "transcript_state"
    );
    const pane_el = target.querySelector("page-pane");
    if (pane_el) {
      pane_el.setAttribute("transcript_state", transcript_state);
      pane_el.setAttribute("lines", lines);
    }
  }

  attributeChangedCallback(key, _, value) {
    if (key == "lines") {
      this.renderPaneLineList(this.shadowRoot);
    }
  }

  toEventHandler(key) {
    if (key === "srt-page/enrich") {
      return ({ detail }) => {
        const listing = this.getAttribute("listing");
        const transcript = JSON.parse(
          this.getAttribute("lines")
        );
        this.setAttribute("lines", JSON.stringify([]));
        const transcript_state = this.getAttribute(
          "transcript_state"
        ).split(" ");
        enrich_all(
          root, listing, transcript, transcript_state
        ).then(({lines, transcript_state}) => {
          this.setAttribute("transcript_state", 
            transcript_state.join(" ")
          );
          this.setAttribute("lines", JSON.stringify(lines));
          const nav_el = this.shadowRoot.querySelector("page-nav");
          nav_el.setAttribute("actions", "new");
        });
      }
    }
  }

}

export { PageData };
