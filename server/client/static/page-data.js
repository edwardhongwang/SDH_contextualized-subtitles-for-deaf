import StyleGlobal from "style-global" with { type: "css" };
import StylePageData from "style-page-data" with { type: "css" };
import { root, get_info } from "api";
import { make_plain } from "api";

class PageData extends HTMLElement {

  static observedAttributes = ["lines", "image"];

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
    const clip_id = this.getAttribute("clip_id");
    const transcript_state = this.getAttribute(
      "transcript_state"
    ).split(" ");
    const info = await get_info(
      root, listing, clip_id, transcript_state, 100
    );
    // TODO: allow other initial transcript states
    make_plain(root, listing, clip_id).then((lines) => {
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
    const image = this.getAttribute("image");
    const clip_id = this.getAttribute("clip_id");
    const transcript_state = this.getAttribute(
      "transcript_state"
    );
    const pane_el = target.querySelector("page-pane");
    if (pane_el) {
      pane_el.setAttribute("transcript_state", transcript_state);
      pane_el.setAttribute("clip_id", clip_id);
      pane_el.setAttribute("image", image);
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
      return async ({ detail }) => {
        const listing = this.getAttribute("listing");
        const clip_id = this.getAttribute("clip_id");
        const transcript = JSON.parse(
          this.getAttribute("lines")
        );
        this.setAttribute("lines", JSON.stringify([]));
        const old_transcript_state = this.getAttribute(
          "transcript_state"
        ).split(" ");
        const { lines, transcript_state } = await detail.api_method(
          root, listing, clip_id, transcript, old_transcript_state
        );
        // Image may update due to transcript state
        const info = await get_info(
          root, listing, clip_id, transcript_state, 100
        );
        this.setAttribute("image", info.image);
        this.setAttribute("transcript_state", 
          transcript_state.join(" ")
        );
        this.setAttribute("lines", JSON.stringify(lines));
        const nav_el = this.shadowRoot.querySelector("page-nav");
        nav_el.setAttribute("actions", "new");
      }
    }
  }

}

export { PageData };
