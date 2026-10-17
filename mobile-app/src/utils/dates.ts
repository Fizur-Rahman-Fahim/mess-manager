import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';

dayjs.extend(utc);

// Bangladesh has no daylight saving, so Asia/Dhaka is always UTC+6.
// We avoid dayjs/plugin/timezone because it relies on Intl time-zone support,
// which is unreliable on Hermes (Android) and produced "Invalid Date".
export const DHAKA_TZ = 'Asia/Dhaka';
const DHAKA_OFFSET_MINUTES = 6 * 60;

export const nowDhaka = () => dayjs.utc().add(DHAKA_OFFSET_MINUTES, 'minute');

export const currentMonth = (): string => nowDhaka().format('YYYY-MM');

export const currentDate = (): string => nowDhaka().format('YYYY-MM-DD');

export const addMonths = (month: string, delta: number): string =>
  dayjs.utc(`${month}-01`).add(delta, 'month').format('YYYY-MM');

export const formatMonthLabel = (month: string): string =>
  dayjs.utc(`${month}-01`).format('MMMM YYYY');

const HAS_OFFSET = /(Z|[+-]\d{2}:?\d{2})$/i;

export const formatDate = (value: string): string => {
  // Date-only values are shown as-is; timestamps with an offset are converted to Dhaka time.
  const parsed = value.length > 10 && HAS_OFFSET.test(value)
    ? dayjs.utc(value).add(DHAKA_OFFSET_MINUTES, 'minute')
    : dayjs.utc(value);
  return parsed.isValid() ? parsed.format('DD MMM YYYY') : value;
};
