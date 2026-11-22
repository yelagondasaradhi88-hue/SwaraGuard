const pptxgen = require('pptxgenjs');

const pres = new pptxgen();

const THEME = {
  name: 'SwaraGuard',
  headFontFace: 'Cambria',
  bodyFontFace: 'Calibri',
  colors: {
    dk1: '0F172A',
    lt1: 'FFFFFF',
    dk2: '1E293B',
    lt2: 'F1F5F9',
    accent1: '0EA5E9',
    accent2: 'F59E0B',
    accent3: 'EF4444',
    accent4: '22C55E',
  },
};

// Helper to add rounded rectangle
function addRoundRect(slide, x, y, w, h, fill) {
  slide.addShape(pptxgen.ShapeType.roundedRectangle, {
    x, y, w, h,
    fill: { color: fill },
    rectRadius: 0.08,
    shadow: { type: 'outer', color: '000000', offset: 4, blur: 6, transparency: 50 },
  });
}

// Helper to add text
function addText(slide, text, { x, y, w, h, size = 16, color = '1E293B', bold = false, align = 'left', fontFace = THEME.bodyFontFace, lineSpacing = 1.0, spacingAfter = 6, bullet = false, isTextBox = true }) {
  slide.addText([{ text: text, options: {} }], {
    x, y, w, h,
    fontSize: size,
    fontFace,
    color,
    bold,
    align,
    lineSpacing,
    spaceAfter: spacingAfter,
    bullet,
    isTextBox,
    margin: 0,
  });
}

// Create a simple test slide
const s1 = pres.addSlide();
addRoundRect(s1, 0, 0, 13.333, 7.5, '0F172A');
addText(s1, 'Test Title', { x: 0.9, y: 1.55, w: 11.5, h: 0.9, size: 54, color: 'FFFFFF', bold: true, fontFace: THEME.headFontFace, align: 'center' });

// Save it
pres.writeFile({ fileName: 'debug_deck.pptx' }).then(() => {
  console.log('Deck written: debug_deck.pptx');
});