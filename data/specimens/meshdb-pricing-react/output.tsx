export default function MeshDbPricingPage() {
  const tiers = [
    {
      name: 'Launch',
      price: '$1.8k',
      detail: '/ month',
      blurb: 'For teams bringing the first regional sync workload to production.',
      bullets: ['3 regions included', '200M synced rows', 'Managed failover'],
      tag: 'TEAM STARTER'
    },
    {
      name: 'Grid',
      price: '$8.4k',
      detail: '/ month',
      blurb: 'For products that need credible cross-region latency and operator controls.',
      bullets: ['12 regions included', '2.5B synced rows', 'Private peering + replay controls'],
      tag: 'DEFAULT PRODUCTION'
    },
    {
      name: 'Sovereign',
      price: 'Custom',
      detail: '',
      blurb: 'For regulated deployments with residency, dedicated control planes, and hands-on support.',
      bullets: ['Regional isolation', 'Dedicated support channel', 'Deployment reviews'],
      tag: 'ENTERPRISE + RESIDENCY'
    }
  ];

  return (
    <main className="bg-[#090b10] text-[#eef2f7] min-h-screen">
      <div className="mx-auto max-w-6xl px-6 pb-24">
        <header className="border-b border-white/10 py-16">
          <p className="mb-3 font-mono text-xs text-[#8793a7]">// pricing without hand-waving</p>
          <div className="grid gap-8 md:grid-cols-[1.05fr_.95fr] md:items-start">
            <div>
              <h1 className="text-5xl font-semibold leading-none">Pay for the grid you actually run.</h1>
              <p className="mt-4 max-w-2xl text-lg text-[#a9b4c6]">
                MeshDB pricing is built around regional sync, operator confidence, and privacy boundaries.
                No toy tiers. No mystery overages. Just clear deployment shapes.
              </p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-[#11151d] p-6">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div><div className="text-3xl font-semibold">14</div><div className="mt-1 text-xs text-[#8793a7]">regions on launch day</div></div>
                <div><div className="text-3xl font-semibold">23ms</div><div className="mt-1 text-xs text-[#8793a7]">median sync latency</div></div>
                <div><div className="text-3xl font-semibold">0</div><div className="mt-1 text-xs text-[#8793a7]">fallback replicas</div></div>
              </div>
            </div>
          </div>
        </header>

        <section className="py-12">
          <p className="mb-2 font-mono text-xs text-[#8793a7]">// the plans</p>
          <div className="grid gap-5 lg:grid-cols-3">
            {tiers.map((tier) => (
              <article key={tier.name} className="rounded-3xl border border-white/10 bg-[#11151d] p-6">
                <div className="mb-3 font-mono text-[10px] tracking-wide text-[#8793a7]">{tier.tag}</div>
                <h2 className="text-2xl font-semibold">{tier.name}</h2>
                <div className="mt-3 text-4xl font-semibold">
                  {tier.price}
                  <span className="ml-1 text-base text-[#8793a7]">{tier.detail}</span>
                </div>
                <p className="mt-4 text-[#a9b4c6]">{tier.blurb}</p>
                <ul className="mt-5 space-y-2 text-sm text-[#d9e4ff]">
                  {tier.bullets.map((bullet) => (
                    <li key={bullet}>◇ {bullet}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>

        <section className="grid gap-5 md:grid-cols-2">
          <div className="rounded-3xl border border-white/10 bg-[#11151d] p-6">
            <p className="mb-2 font-mono text-xs text-[#8793a7]">// the mechanism</p>
            <pre className="overflow-auto rounded-2xl border border-white/10 bg-[#0d1017] p-4 text-sm text-[#dbe6ff]">
{`meshdb regions enable \
  --plan grid \
  --regions us-east-1,eu-west-1,ap-southeast-1`}
            </pre>
          </div>
          <div className="rounded-3xl border border-white/10 bg-[#11151d] p-6">
            <p className="mb-2 font-mono text-xs text-[#8793a7]">// enterprise mechanics</p>
            <p className="text-[#a9b4c6]">
              Sovereign deployments include residency-aware region maps, audited replay controls, and direct architecture review.
            </p>
            <div className="mt-6 flex gap-3">
              <a className="rounded-xl bg-[#eef2ff] px-4 py-2 font-semibold text-[#05070b]" href="#contact-sales">
                Talk to sales
              </a>
              <a className="rounded-xl border border-white/10 px-4 py-2 text-[#dbe6ff]" href="#start-grid">
                Start with Grid
              </a>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
