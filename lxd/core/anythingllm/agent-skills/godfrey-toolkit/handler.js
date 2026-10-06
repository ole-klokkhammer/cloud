module.exports.runtime = {
  handler: async ({ args, AnythingLLM }) => {
    const query = args?.query || "";

    // Pseudocode: load/search only the intended source
    // Exact APIs depend on the AnythingLLM skill runtime version you are using.
    const result = await AnythingLLM.documents.search({
      query,
      filters: {
        source: "personalized-learning-policy.md"
      }
    });

    return {
      success: true,
      content: result
    };
  }
};