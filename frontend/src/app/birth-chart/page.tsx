'use client';

import { BirthChartPage } from '@/components/birth-chart';
import { useGenerateChart } from '@/hooks/use-birth-chart';
import { useBirthChartStore } from '@/stores/birthChartStore';

export default function BirthChartRoutePage() {
  const { mutate: generateChart, isPending } = useGenerateChart();
  const { currentChart } = useBirthChartStore();

  const handleGenerateChart = (input: Parameters<typeof generateChart>[0]) => {
    generateChart(input);
  };

  return (
    <BirthChartPage
      chart={currentChart ? { id: currentChart.id, palaces: currentChart.palaces } : null}
      isLoading={isPending}
      onGenerateChart={handleGenerateChart}
    />
  );
}
