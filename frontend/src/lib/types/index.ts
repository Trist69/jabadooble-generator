export interface Symbol {
  id: string;
  label: string;
  url: string;
  thumbnail_url?: string;
  cartoonized_url?: string;
  cartoonized: boolean;
}

export interface Library {
  id: string;
  name: string;
  theme: string;
  symbols: Symbol[];
}

export interface SymbolPlacement {
  label: string;
  url: string;
  cx: number;
  cy: number;
  size: number;
}

export interface GameCard {
  index: number;
  placements: SymbolPlacement[];
}

export interface Game {
  id: string;
  library_id: string;
  order: number;
  total_cards: number;
  cards: GameCard[];
}

export interface AppSettings {
  gemini_api_key_set: boolean;
  xai_api_key_set: boolean;
  ai_provider: string;
  gemini_model: string;
  xai_model: string;
  generation_style: string;
}

export interface AiGenerateProgress {
  done: number;
  total: number;
  library: Library;
}
