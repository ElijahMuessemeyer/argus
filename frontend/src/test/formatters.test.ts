import { formatPrice, formatPercent, formatCompactNumber } from '../utils/formatters';

const stripNonAscii = (value: string) => value.replace(/[\u00A0]/g, ' ');

describe('formatters', () => {
  it('formats prices as USD currency', () => {
    const formatted = stripNonAscii(formatPrice(1234.56));
    expect(formatted).toContain('$1,234.56');
  });

  it('formats percents with sign and two decimals', () => {
    expect(formatPercent(5)).toBe('+5.00%');
    expect(formatPercent(-2.5)).toBe('-2.50%');
  });

  it('formats compact numbers', () => {
    expect(formatCompactNumber(1_500)).toBe('1.50K');
    expect(formatCompactNumber(2_500_000)).toBe('2.50M');
  });
});
