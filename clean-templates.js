const fs = require('fs');
const path = require('path');

const templateDir = path.join(__dirname, 'templates');


fs.readdirSync(templateDir).forEach(file => {
  const filePath = path.join(templateDir, file);

  if (path.extname(file) === '.html') {
    let content = fs.readFileSync(filePath, 'utf8');

    const cleaned = content.replace(/align\s*=\s*"(left|right|center)"/gi, (_, alignVal) => {
      return `style="text-align: ${alignVal.toLowerCase()};"`;
    });

    fs.writeFileSync(filePath, cleaned, 'utf8');
    console.log(`Updated: ${file}`);
  }
});
