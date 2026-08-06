import useCampaigns from '../hooks/useCampaigns'
import SkeletonLoader from '../components/SkeletonLoader'
import ErrorFallback from '../components/ErrorFallback'
import CampaignSummaryCard from '../components/campaign/CampaignSummaryCard'
import RelationshipGraph from '../components/campaign/RelationshipGraph'
import ConnectedDomainsTable from '../components/campaign/ConnectedDomainsTable'
import InfrastructureCard from '../components/campaign/InfrastructureCard'
import EvidenceTable from '../components/campaign/EvidenceTable'
import ConfidenceCard from '../components/campaign/ConfidenceCard'
import CampaignTimeline from '../components/campaign/CampaignTimeline'

export default function Campaigns() {
  const { campaigns, loading, error, refetch } = useCampaigns()

  if (loading) return <SkeletonLoader />
  if (error) return <ErrorFallback message={error} onRetry={refetch} />
  if (!campaigns) return null

  const { summary, connectedDomains, infrastructure, sharedEvidence, confidence, timeline } = campaigns

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#f1f5f9]">Campaign Correlation & Attribution</h1>
        <p className="text-xs text-slate-400">
          Analyze malicious campaign clusters, group domain footprints by nameservers, and map coordinated infrastructure links.
        </p>
      </div>

      {/* Campaign Summary overview */}
      <CampaignSummaryCard summary={summary} />

      {/* Grid panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left Side: Topology Visualizer, Connected Domains, and Evidence log */}
        <div className="lg:col-span-2 space-y-6">
          <RelationshipGraph />
          
          <ConnectedDomainsTable domains={connectedDomains} />
          
          <EvidenceTable evidence={sharedEvidence} />
        </div>

        {/* Right Side: Verdict Engine, Shared Infrastructure specifications, and History Timeline */}
        <div className="space-y-6">
          <ConfidenceCard confidence={confidence} />
          
          <InfrastructureCard infrastructure={infrastructure} />
          
          <CampaignTimeline timeline={timeline} />
        </div>
      </div>
    </div>
  )
}
