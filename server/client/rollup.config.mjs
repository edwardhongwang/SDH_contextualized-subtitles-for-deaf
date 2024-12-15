import fs from 'fs';
import path from 'path';
import copy from 'rollup-plugin-copy'
import alias from '@rollup/plugin-alias';
import { parse } from 'node-html-parser';
import css from "rollup-plugin-import-css";

const to_path = (dirname, fname) => {
  return path.join(process.cwd(), dirname, fname)
}

const split = fname => fname.split(path.sep)
const is_clip = fname => !isNaN(parseInt(split(fname).pop()))

const info_index = fs.readdirSync(
  to_path('api', 'make'), { recursive: true }
).filter(is_clip).map(split).reduce(
  (info_index, [listing, clip_id]) =>  {
    const info = info_index[listing] || {};
    const clip_count = Math.max(
      parseInt(clip_id)+1, info.clip_count || 0
    )
    return {
      ...info_index, [listing]: { clip_count }
    }
  },
  {}
);

const update_info = info => {
  const { clip_count } = info_index[info.listing] || {
    clip_count: 0
  };
  return { ...info, clip_count };
}

const to_entries = (index_string) => {
  const index = parse(index_string)
  const importmap_el = index.querySelector('script[type=importmap]');
  return Object.entries(
    JSON.parse(importmap_el.innerHTML).imports
  ).map(
    ([find,fname]) => ({ find, replacement: to_path('static', fname)})
  );
}

const transform = (index_string) => {
  const index = parse(index_string)
  const importmap_el = index.querySelector('script[type=importmap]');
  importmap_el.innerHTML = `
      {
        "imports": {
          "index": "./index.js"
        }
      }
      `;
  return index.toString();
}

const entries = to_entries(
  fs.readFileSync(to_path('static', 'index.html'), 'utf8')
);
export default {
  input: "static/index.js",
  plugins: [
    copy({
      targets: [{
        src: 'static/index.html',
        dest: 'dist',
        transform 
      },{
        src: 'api', dest: 'dist',
      },{
        src: 'api/index/info', dest: 'dist/api/index',
        transform: (content) => JSON.stringify(
          JSON.parse(content).map(update_info).filter(
            info => info.clip_count > 0
          )
        )
      },{
        src: 'data', dest: 'dist'
      },{
        src: 'static/*.webmanifest', dest: 'dist'
      },{
        src: 'static/*.woff2', dest: 'dist'
      },{
        src: 'static/*.ico', dest: 'dist'
      },{
        src: 'static/*.png', dest: 'dist'
      }]
    }),
    css(), alias({ entries })
  ],
  output: {
    file: "dist/index.js",
    format: "esm"
  }
};
