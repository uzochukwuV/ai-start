
import DefaultLayout from "@/layouts/default";

import React, { Suspense, lazy } from 'react';
const SchoolPerformanceDashboard = lazy(() => import('@/components/performance-chart'));
const TopSchools = lazy(() => import('@/components/school-metrics'));

export default function IndexPage() {
  return (
    <DefaultLayout>
      <section className="flex items-center justify-center gap-4 py-8 md:py-10">
      <Suspense fallback={<div>Loading component 2...</div>}>
          <SchoolPerformanceDashboard />
        </Suspense>
       <div>
       <Suspense fallback={<div>Loading component 2...</div>}>
          <TopSchools route={"top_schools"} />
        </Suspense>
        <Suspense fallback={<div>Loading component 2...</div>}>
          <TopSchools route={"bottom_schools"} />
        </Suspense>
       </div>
        
      </section>
    </DefaultLayout>
  );
}
