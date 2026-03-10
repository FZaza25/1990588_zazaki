export const CHART_WINDOW_SECONDS = 300
export const CHART_STEP_SECONDS = 5
export const CHART_MAX_POINTS = CHART_WINDOW_SECONDS / CHART_STEP_SECONDS + 1

export const chartTime = Array.from(
  { length: CHART_MAX_POINTS },
  (_, index) => index * CHART_STEP_SECONDS
)
