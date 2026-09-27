/**
 * Sudoku API Skill
 * Tool-call compatible implementation for external LLMs.
 * Supports OpenAI Tool Calls, Anthropic Tool Use, and generic JSON Schema tools.
 */

const BASE_URL = "https://www.sudoku100.com";

const DIFFICULTIES = ["beginner", "easy", "medium", "hard", "expert", "extreme"];
const FORMATS = ["png", "webp", "svg", "jpg"];
const ACTIONS = ["generate", "get_by_id", "list_difficulties"];

const DIFFICULTY_INFO = [
  { level: "beginner", hints: "45-50", description: "For beginners" },
  { level: "easy", hints: "38-44", description: "Simple puzzles" },
  { level: "medium", hints: "32-37", description: "Moderate difficulty" },
  { level: "hard", hints: "26-31", description: "Challenging puzzles" },
  { level: "expert", hints: "20-25", description: "Expert level" },
  { level: "extreme", hints: "17-19", description: "Most challenging" }
];

class SudokuApiError extends Error {
  constructor(message, code = "INVALID_PARAMETER") {
    super(message);
    this.name = "SudokuApiError";
    this.code = code;
  }
}

const SudokuApiSkill = {
  name: "sudoku_api",
  version: "1.1.0",
  description:
    "Generate and retrieve Sudoku puzzle images through the Sudoku100 API. " +
    "Supports 6 difficulty levels (beginner to extreme), retrieval by puzzle ID (1-10000), " +
    "adjustable image width (100-1000px), and multiple image formats (png, webp, svg, jpg). " +
    "No API key required; every puzzle has a guaranteed unique solution.",

  // JSON Schema shared by all providers
  inputSchema: {
    type: "object",
    properties: {
      action: {
        type: "string",
        description: "Action to perform: generate, get_by_id, or list_difficulties",
        enum: ACTIONS,
        default: "generate"
      },
      difficulty: {
        type: "string",
        description: "Difficulty level for the generated puzzle",
        enum: DIFFICULTIES
      },
      id: {
        type: "integer",
        description: "Sudoku puzzle ID (1-10000), required for get_by_id",
        minimum: 1,
        maximum: 10000
      },
      width: {
        type: "integer",
        description: "Image width in pixels (100-1000)",
        minimum: 100,
        maximum: 1000,
        default: 500
      },
      format: {
        type: "string",
        description: "Image format",
        enum: FORMATS,
        default: "png"
      }
    }
  },

  /**
   * Invoke the tool. Accepts either a params object or a JSON string
   * (OpenAI tool calls deliver `function.arguments` as a JSON string).
   *
   * @param {Object|string} input
   * @returns {Promise<{success: boolean, data?: Object, error?: {message: string, code: string}}>}
   */
  invoke: async function (input) {
    try {
      const params = typeof input === "string" ? JSON.parse(input) : (input || {});

      const action = params.action || "generate";
      const width = params.width !== undefined ? params.width : 500;
      const format = params.format || "png";

      if (!ACTIONS.includes(action)) {
        throw new SudokuApiError(
          `Invalid action '${action}'. Must be one of: ${ACTIONS.join(", ")}`,
          "INVALID_ACTION"
        );
      }
      if (params.difficulty !== undefined && !DIFFICULTIES.includes(params.difficulty)) {
        throw new SudokuApiError(
          `Invalid difficulty '${params.difficulty}'. Must be one of: ${DIFFICULTIES.join(", ")}`,
          "INVALID_DIFFICULTY"
        );
      }
      if (params.id !== undefined) {
        if (!Number.isInteger(params.id) || params.id < 1 || params.id > 10000) {
          throw new SudokuApiError(
            `Invalid id '${params.id}'. Must be an integer between 1 and 10000`,
            "INVALID_ID"
          );
        }
      }
      if (!Number.isInteger(width) || width < 100 || width > 1000) {
        throw new SudokuApiError(
          `Invalid width '${width}'. Must be an integer between 100 and 1000`,
          "INVALID_WIDTH"
        );
      }
      if (!FORMATS.includes(format)) {
        throw new SudokuApiError(
          `Invalid format '${format}'. Must be one of: ${FORMATS.join(", ")}`,
          "INVALID_FORMAT"
        );
      }

      if (action === "list_difficulties") {
        return {
          success: true,
          data: {
            difficulties: DIFFICULTY_INFO,
            message: "Available difficulty levels"
          }
        };
      }

      if (action === "get_by_id") {
        if (params.id === undefined) {
          throw new SudokuApiError(
            "Parameter 'id' is required for get_by_id action",
            "MISSING_ID"
          );
        }
        return {
          success: true,
          data: {
            url: `${BASE_URL}/img-id/${params.id}?width=${width}&format=${format}`,
            id: params.id,
            width,
            format,
            message: "Sudoku puzzle retrieved successfully"
          }
        };
      }

      // generate (default)
      let url;
      if (params.id !== undefined) {
        // Generate with a specific puzzle ID
        url = `${BASE_URL}/img-id/${params.id}?width=${width}&format=${format}`;
      } else if (params.difficulty) {
        url = `${BASE_URL}/sudoku-img/${params.difficulty}?width=${width}&format=${format}`;
      } else {
        url = `${BASE_URL}/sudoku-img?width=${width}&format=${format}`;
      }

      return {
        success: true,
        data: {
          url,
          id: params.id,
          difficulty: params.difficulty || "random",
          width,
          format,
          message: "Sudoku puzzle generated successfully"
        }
      };
    } catch (error) {
      if (error instanceof SudokuApiError) {
        return { success: false, error: { message: error.message, code: error.code } };
      }
      return {
        success: false,
        error: {
          message: error.message || "Unknown error occurred",
          code: error.code || "EXECUTION_ERROR"
        }
      };
    }
  },

  /**
   * Get the tool definition in a provider-specific format.
   *
   * @param {"openai"|"anthropic"|"generic"} [provider="openai"]
   * @returns {Object}
   */
  getToolDefinition: function (provider = "openai") {
    const base = {
      name: this.name,
      description: this.description
    };
    if (provider === "anthropic") {
      return { ...base, input_schema: this.inputSchema };
    }
    if (provider === "generic") {
      return { ...base, parameters: this.inputSchema };
    }
    // OpenAI function calling format
    return {
      type: "function",
      function: { ...base, parameters: this.inputSchema }
    };
  },

  // Legacy execute method for backward compatibility
  execute: async function (params) {
    return this.invoke(params);
  },

  // Get available actions
  getAvailableActions: function () {
    return [...ACTIONS];
  }
};

module.exports = SudokuApiSkill;

// CLI entry: node sudoku-api-skill.js [--difficulty hard] [--id 238] [--width 800] [--format webp] [--action generate]
if (require.main === module) {
  const args = process.argv.slice(2);
  const params = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = String(args[i] || "").replace(/^--/, "");
    const value = args[i + 1];
    if (key === "id" || key === "width") {
      params[key] = parseInt(value, 10);
    } else {
      params[key] = value;
    }
  }
  SudokuApiSkill.invoke(params).then((result) => {
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.success ? 0 : 1);
  });
}
