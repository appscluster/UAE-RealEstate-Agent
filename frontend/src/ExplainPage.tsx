const BEATS = [
  {
    title: 'The problem',
    body: 'The category is Dubai off plan deal readiness. Sandstone Realty has to reconcile a brochure, an SPA extract, a payment schedule, and a simulated project status before anyone calls a price fair. A price inside the comparables can still be the wrong answer when construction has stalled. A Dubai checklist is the wrong pack for an Abu Dhabi Aldar sale.',
  },
  {
    title: 'The solution',
    body: 'The app is React and FastAPI, with a code first LangGraph loop: plan, specialists, critic, one repair, then the deal writer. LangGraph keeps that path testable. The writer asks OmniRoute for the prose when a model is selected. The critic and the price flag stay in code. The agent never pays a buyer and never queries DLD.',
  },
  {
    title: 'The live demo',
    body: 'Open Canal Courtyard. Read the deal. You should see the beneficiary mismatch, the unit mismatch, the stalled status, and a report that does not call the price fair. Then approve it. Then check an Abu Dhabi sale and read the jurisdiction line. Then open Creek Lane, where the report does call the price fair.',
  },
  {
    title: 'Challenges and learnings',
    body: 'A stalled file inside the comparables must not be called fair, even when the model says it is. A request for another brokerage is refused and audited. An Abu Dhabi question is answered by a reviewer. The reply comes from the model through OmniRoute when that model can answer on chat completions, and the log shows that call\'s token count. The build is a working prototype.',
  },
  {
    title: 'The vision',
    body: 'A DataRobot customer in a Dubai brokerage has this review every time a file is ready for an offer. Productize the loop as a governed template: one brokerage, seeded documents with citations, a critic that blocks a false fair price, a human decision, and an audit. A second emirate is a new pack, reviewed on its own. Scale the template. Keep the person in the decision.',
  },
]

const LOOKING = [
  {
    title: 'Problem solving acumen',
    body: 'The problem is a brokerage conflict a coordinator has to settle. Valuation can sit inside the comparables while off plan risk says construction has stalled. The critic catches that, and the writer leaves the conflict in the report.',
  },
  {
    title: 'Strategic vision',
    body: 'The same loop is the product a customer would pilot: cited evidence, a human gate, and an audit. Jurisdiction packs stay separate. A Dubai checklist is never treated as an Abu Dhabi approval. The page promises no residency, no savings, and no live official check.',
  },
  {
    title: 'Technical credibility',
    body: 'The desk is a complete application. React on port 43231, FastAPI on port 54231, LangGraph in agent/runner.py, and Server Sent Events for the log. pytest covers the critic, the tenant wall, the model guard, and the decisions.',
  },
  {
    title: 'Creativity and passion',
    body: 'The visible moment is one specialist catching another. The valuation finding and the stalled status are each reasonable alone. Together they block a fair price. The Abu Dhabi button answers with a reviewer while the open Dubai file is still read.',
  },
]

const CODE_FIRST = [
  { name: 'Start', body: 'Read the deal calls run_deal in agent/runner.py with Sandstone Realty, the open file, and the selected model.' },
  { name: 'Planner', body: 'Checks the request is still inside Sandstone Realty. A cross tenant file stops here. An Abu Dhabi, Aldar, or Modon question adds the jurisdiction reviewer.' },
  { name: 'Specialists', body: 'Permit, valuation, cost, and off plan risk read the seeded documents in code. The jurisdiction reviewer, when assigned, states that this Dubai checklist does not validate an Abu Dhabi Aldar sale.' },
  { name: 'Critic', body: 'Raises stalled price, handover dates, beneficiary mismatch, and unit id when the documents disagree. One repair reads the same documents again and invents no date or price.' },
  { name: 'Deal writer', body: 'Uses the template, or asks OmniRoute. A blocked price cannot be called fair. An Abu Dhabi sale cannot be marked validated. The log records the model id and the token count from the response.' },
  { name: 'End', body: 'The run returns the draft. Approve, Send it back, or Escalate is a person, after the graph has finished.' },
]

const SERVED = [
  {
    name: 'Transaction coordinator',
    who: 'The person signed in on this desk. They are the only user of the product.',
    how: 'They pick a file, choose a model, watch the agent plan and the specialists report, then Approve, Send it back, or Escalate. The log shows each step while the run is still going.',
  },
  {
    name: 'Manager',
    who: 'The person who accepts a report for the file. In this demo the decision is stored as manager:demo.',
    how: 'Approve stores the report and says it is accepted for this file. Nothing is sent to a buyer, and no payment is approved.',
  },
  {
    name: 'Pod lead',
    who: 'The coordinator\'s lead, when a case should not be closed on the desk.',
    how: 'Escalate records the case for the pod lead. It does not send a message, and it does not contact a buyer.',
  },
  {
    name: 'Buyer',
    who: 'A fictional person named on the file, such as buyer SYN-12 on Creek Lane or buyer SYN-19 on Palm Walk. They are a row in the question, not a user of Readiness.',
    how: 'They do not sign in. This desk never sends them the report and never pays a unit.',
  },
  {
    name: 'Another brokerage',
    who: 'A second customer on the same platform. This desk is Sandstone Realty only. Other Broker owns the file deal_other_broker.',
    how: 'Their file stays in their own tenant. A request from this desk to read it is refused and written to the audit.',
  },
]

const PATH = [
  { name: 'File', body: 'The seeded documents are the brochure, the SPA extract, the payment schedule, the simulated project status, and the comparables. Every document says SYNTHETIC DEMO. The status record says NOT ISSUED BY DLD.' },
  { name: 'Specialists', body: 'Permit compares beneficiary references and the schedule unit. Valuation places the asking price against the seeded comparables. Cost lists the asking price, a 4 percent DLD fee assumption, and a 2 percent agency fee assumption, each marked to verify. Off plan risk reads the stalled or progressing status and the handover wording.' },
  { name: 'Critic', body: 'Canal Courtyard and Palm Walk are inside a progressing comparable range and the status says stalled, so the price is not fair. Creek Lane is progressing and the report calls the price fair. Handover, beneficiary, and unit conflicts stay as warnings.' },
  { name: 'Readiness', body: 'The coordinator opens the file. The agent plans, the specialists report, the critic checks, and the writer drafts through OmniRoute or the template. Official links for Dubai REST, project status, and RERA ecard verification are manual links only. This desk does not query them.' },
  { name: 'Decision', body: 'Approve accepts the report for the file. Send it back returns it to the coordinator. Escalate records it for the pod lead. Nothing is sent.' },
  { name: 'Jurisdiction', body: 'Check an Abu Dhabi sale asks whether this Dubai checklist can validate an Abu Dhabi Aldar sale. The reviewer answers that it cannot. No Abu Dhabi pack is loaded, and no official service is queried. The open Dubai file is still read.' },
  { name: 'Tenant wall', body: 'No run reads another brokerage\'s file. A cross tenant request is refused and written to the audit.' },
]

const TOOLS = [
  { name: 'React', how: 'The sign in, this explanation, and the coordinator desk are React 18 components.', why: 'The assignment asks for a complete application a person can use, not a script that only prints a report.' },
  { name: 'Vite', how: 'Vite builds the React app and serves it on port 43231 during development. In development the page calls the API through the Vite proxy.', why: 'The desk has to build cleanly into a static bundle the container can host.' },
  { name: 'serve', how: 'The frontend image uses the serve package to host the built files on port 43231.', why: 'The demo should open in a browser from one Compose stack, with no extra web server to install.' },
  { name: 'Figtree and Literata', how: 'Fontsource ships Figtree for the interface and Literata for the titles.', why: 'The type stays inside the bundle, so the desk does not depend on a font service.' },
  { name: 'FastAPI', how: 'FastAPI serves the session, the deal files, the model list, the run, the scope check, the decision, and the audit.', why: 'The agent needs one backend the desk can call, with the tenant bound on the server.' },
  { name: 'Uvicorn', how: 'Uvicorn runs the FastAPI app on port 54231.', why: 'The API has to stay up as its own process beside the frontend.' },
  { name: 'Pydantic', how: 'FastAPI uses Pydantic to read JSON bodies before a route runs.', why: 'A bad payload should fail at the door instead of halfway through a run.' },
  { name: 'LangGraph', how: 'The readiness run is a LangGraph graph: planner, specialists, critic, one repair, and the deal writer. The state they share is DealState in agent/runner.py.', why: 'The assignment asks for a code first agent. A fixed graph keeps that loop testable and visible on the desk.' },
  { name: 'LangChain Core', how: 'LangGraph is pinned beside LangChain Core. The deal writer calls the gateway with the standard library.', why: 'The graph runtime needs that library to compile and invoke the nodes.' },
  { name: 'sse-starlette', how: 'After Read the deal, the desk opens a Server Sent Events stream at /runs/{id}/events and paints each step as it is recorded.', why: 'The coordinator should see the plan, the findings, the critic, and the writer, not one silent wait.' },
  { name: 'SQLite', how: 'SQLite holds the audit log and human decisions under backend/var.', why: 'One file is enough for the demo, and every row stays with its tenant. There is no separate database to operate.' },
  { name: 'Docker Compose', how: 'Compose builds and runs the frontend on port 43231 and the backend on port 54231. The backend reaches OmniRoute on the host through host.docker.internal.', why: 'The interview demo should start as one stack.' },
  { name: 'OmniRoute', how: 'The writer calls the local OmniRoute gateway at /v1/chat/completions. The picker defaults to auto/chat. The template stays available when the gateway is down. The log shows the model name and the token count from the response. This repo does not change OmniRoute.', why: 'The report has to be written by a model when one is selected. OmniRoute is the gateway already running here, so the agent does not keep provider keys of its own.' },
  { name: 'pytest', how: 'pytest runs the Canal Courtyard critic, the scope refusals, the model guard, the decision API, and the page contract.', why: 'The guard and the story have to stay true when the desk changes.' },
]

export function ExplainPage() {
  const signedIn = localStorage.getItem('readiness-session') === 'coordinator'
  return (
    <main className="explain">
      <div className="explain-body">
        <header className="mast">
          <div>
            <p className="eyebrow">Sandstone Realty · Dubai</p>
            <h1>How this meets the assignment</h1>
          </div>
          <div>
            <span className="seal">SYNTHETIC DEMO</span>
            <div className="row">
              <a className="texty" href="/">Open the desk</a>
            </div>
          </div>
        </header>
        <p className="lede">
          The brief asks for a problem, a code first agent with a frontend and a backend, and a short talk: the problem, the solution, a live demo, the challenges, and how you would productize it for a DataRobot customer.
        </p>
        {!signedIn ? <p className="warning">Sign in on the desk as coordinator / demo, then return here.</p> : null}
        <div className="explain-grid">
          {BEATS.map((item) => (
            <article key={item.title}>
              <h2>{item.title}</h2>
              <p>{item.body}</p>
            </article>
          ))}
        </div>
        <section aria-labelledby="looking-heading">
          <h2 id="looking-heading">What the review looks for</h2>
          <div className="explain-grid">
            {LOOKING.map((item) => (
              <article key={item.title}>
                <h3>{item.title}</h3>
                <p>{item.body}</p>
              </article>
            ))}
          </div>
        </section>
        <section aria-labelledby="code-first-heading">
          <h2 id="code-first-heading">Code first</h2>
          <p className="lede">
            The agent is a Python program. LangGraph compiles the nodes in agent/runner.py. The state they share is the typed DealState in that file: tenant, deal, question, findings, critic, draft, and whether the planner refused. Tests call the same functions.
          </p>
          <ol>
            {CODE_FIRST.map((step) => (
              <li key={step.name}>
                <strong>{step.name}</strong>
                <p>{step.body}</p>
              </li>
            ))}
          </ol>
        </section>
        <section aria-labelledby="served-heading">
          <h2 id="served-heading">Who this serves</h2>
          <p className="lede">
            Readiness serves the brokerage staff who have to decide whether a synthetic file is ready for an offer. Buyers are the subject of the question. They are not the audience of the report.
          </p>
          <div className="explain-grid">
            {SERVED.map((person) => (
              <article key={person.name}>
                <h3>{person.name}</h3>
                <p><strong>Who.</strong> {person.who}</p>
                <p><strong>How.</strong> {person.how}</p>
              </article>
            ))}
          </div>
        </section>
        <section aria-labelledby="path-heading">
          <h2 id="path-heading">The path</h2>
          <p className="lede">
            Buyers exist only as names on the question. The report is for the coordinator and the manager. A Dubai checklist does not validate an Abu Dhabi sale.
          </p>
          <div className="explain-grid">
            {PATH.map((step) => (
              <article key={step.name}>
                <h3>{step.name}</h3>
                <p>{step.body}</p>
              </article>
            ))}
          </div>
        </section>
        <section aria-labelledby="tools-heading">
          <h2 id="tools-heading">The tools</h2>
          <p className="lede">The tools this running desk uses, what each one does here, and why it is in the stack.</p>
          <div className="explain-grid tools">
            {TOOLS.map((tool) => (
              <article key={tool.name}>
                <h3>{tool.name}</h3>
                <p><strong>How.</strong> {tool.how}</p>
                <p><strong>Why.</strong> {tool.why}</p>
              </article>
            ))}
          </div>
        </section>
        <p className="end"><a className="solid" href="/">Open the desk</a></p>
      </div>
    </main>
  )
}
