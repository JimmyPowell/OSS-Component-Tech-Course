/**
 * 链接转换工具函数
 * 将文本中的URL自动转换为可点击的HTML链接
 */

/**
 * 将文本中的URL转换为HTML链接
 * @param {string} text - 包含URL的原始文本
 * @returns {string} - 转换后的HTML字符串
 */
export function convertLinksToHtml(text) {
  if (!text) return text;
  
  // URL正则表达式，匹配http://和https://开头的链接
  const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`\[\]]*[^\s<>"{}|\\^`\[\].,!?;:])/g;
  
  // 将URL替换为HTML链接
  return text.replace(urlRegex, (url) => {
    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="content-link">${url}</a>`;
  });
}

/**
 * 处理换行符，将\n转换为<br>标签
 * @param {string} text - 包含换行符的文本
 * @returns {string} - 转换后的HTML字符串
 */
export function convertNewlinesToBr(text) {
  if (!text) return text;
  return text.replace(/\n/g, '<br>');
}

/**
 * 综合处理文本：转换链接和换行符
 * @param {string} text - 原始文本
 * @returns {string} - 处理后的HTML字符串
 */
export function processTextContent(text) {
  if (!text) return text;
  
  // 先转换链接，再处理换行
  let processed = convertLinksToHtml(text);
  processed = convertNewlinesToBr(processed);
  
  return processed;
}