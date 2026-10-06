module.exports.runtime = {
  handler: async ({ args, AnythingLLM }) => {
    // Look for URL in args.url or args.query
    const url = args?.url || args?.query;
    
    if (!url) {
      return {
        success: false,
        content: "No URL was provided. Please provide a valid URL to analyze."
      };
    }

    try {
      const response = await fetch(url);
      if (!response.ok) {
        return {
          success: false,
          content: `Failed to fetch the page. HTTP Status: ${response.status}`
        };
      }
      
      const html = await response.text();
      
      // Simple text extraction:
      // 1. Remove script and style elements
      // 2. Remove all HTML tags
      // 3. Normalize whitespace
      const text = html
        .replace(/<script\b[^>]*>([\S\s]*?)<\/script>/gim, "")
        .replace(/<style\b[^>]*>([\S\s]*?)<\/style>/gim, "")
        .replace(/<[^>]+>/g, " ")
        .replace(/\s+/g, " ")
        .trim();

      return {
        success: true,
        content: text
      };
    } catch (error) {
      return {
        success: false,
        content: `An error occurred while fetching the webpage: ${error.message}`
      };
    }
  }
};