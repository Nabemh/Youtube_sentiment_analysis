
export interface SentimentComponents {
  transcript_mean: number;
  comments_mean: number;
  engagement: number;
}

export interface SentimentData {
  video_id: string;
  score: number;
  label: string;
  components: SentimentComponents;
  model_accuracy: number;
}

export enum AnalysisStatus {
  IDLE = 'IDLE',
  LOADING = 'LOADING',
  SUCCESS = 'SUCCESS',
  ERROR = 'ERROR'
}
