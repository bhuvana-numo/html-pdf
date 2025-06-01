const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

const templatesDir = './templates';

fs.readdirSync(templatesDir).forEach(file => {
  if (file.endsWith('.html')) {
    const filePath = path.join(templatesDir, file);
    const html = fs.readFileSync(filePath, 'utf-8');
    const $ = cheerio.load(html);

    $('[align]').each((_, el) => {
      const align = $(el).attr('align');
      const style = $(el).attr('style') || '';
      $(el).removeAttr('align');
      $(el).attr('style', `text-align: ${align}; ${style}`.trim());
    });

    fs.writeFileSync(filePath, $.html());
    console.log(`Cleaned: ${file}`);
  }
});
