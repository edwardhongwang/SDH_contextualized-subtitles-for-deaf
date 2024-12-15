import layoutCSS from 'style-layout' with { type: 'css' };
import fontsCSS from 'style-fonts' with { type: 'css' };

const styles = () => {
  document.adoptedStyleSheets = [
    layoutCSS, fontsCSS
  ];
}

export { styles }
