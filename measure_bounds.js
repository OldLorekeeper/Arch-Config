const fs = require('fs');
const paper = require('paper');

paper.setup(new paper.Size(200, 200));

const svgDir = '/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/';
const files = fs.readdirSync(svgDir).filter(f => f.endsWith('.svg'));

files.forEach(file => {
    const content = fs.readFileSync(svgDir + file, 'utf-8');
    
    // We want to remove the shadow group to only measure the main shapes
    // A simple regex to remove <g opacity="0.2">...</g>
    const cleanContent = content.replace(/<g[^>]*opacity="0\.2"[^>]*>[\s\S]*?<\/g>/, '');
    
    paper.project.clear();
    const item = paper.project.importSVG(cleanContent);
    
    const bounds = item.bounds;
    console.log(`${file}: X=[${bounds.x.toFixed(1)}, ${(bounds.x + bounds.width).toFixed(1)}] (W=${bounds.width.toFixed(1)}), Y=[${bounds.y.toFixed(1)}, ${(bounds.y + bounds.height).toFixed(1)}] (H=${bounds.height.toFixed(1)})`);
});
