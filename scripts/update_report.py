"""Update the existing report body for P_014 while preserving its edited cover.
Uses OOXML edits so styles, relationships and cover content remain intact.
Requires lxml and Pillow; run with the project's document-authoring Python.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
import hashlib, json
from lxml import etree as E
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'submission/VenueVista-Project-Report.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';NS={'w':W}
def tag(t):return '{'+W+'}'+t
with ZipFile(path) as z: entries={i.filename:(i,z.read(i.filename)) for i in z.infolist()}
root=E.fromstring(entries['word/document.xml'][1]);body=root.find('w:body',NS)
def text(el):return ''.join(el.xpath('.//w:t/text()',namespaces=NS))
if any(text(x)=='Project registration and Oracle database' for x in body):
    print('Report body already updated; keeping the existing report and cover.');raise SystemExit(0)
cut=next(i for i,x in enumerate(body) if text(x)=='Abstract')
cover_before=[E.tostring(x) for x in list(body)[:cut]]
# Find existing body formatting instead of replacing document-wide styles.
normal=deepcopy(list(body)[cut+1]);heading1=deepcopy(next(x for x in body if text(x)=='Requirements and scope'))
heading2=deepcopy(next(x for x in body if text(x)=='Problem statement'))
def newp(value,template=normal):
    p=deepcopy(template)
    for child in list(p):
        if child.tag!=tag('pPr'):p.remove(child)
    r=E.SubElement(p,tag('r'));t=E.SubElement(r,tag('t'));t.text=value
    return p

def settext(el,value):
    nodes=el.xpath('.//w:t',namespaces=NS)
    if nodes:
        nodes[0].text=value
        for n in nodes[1:]:n.text=''

def breakpage():
    p=E.Element(tag('p'));r=E.SubElement(p,tag('r'));br=E.SubElement(r,tag('br'));br.set(tag('type'),'page');return p

special={
 'Event organizers need a consistent answer': 'Organizers need consistent seat availability, guest admission and confirmed revenue. Separate spreadsheets can promise seats twice, miss inventory released by cancellations and include invalid sales. VenueVista maintains these records together for event and media operations.',
 'The implemented user is an event organizer': 'The evaluator uses a local organizer console to create venues and events, confirm bookings, and compare seating, guest lists and analytics. Payment is simulated; no merchant account or email service is required.',
 'The Maven integration suite ran against': 'The integration suite passed on isolated H2 storage and an Oracle Database Free test schema. Each database run completed 12 tests with zero failures, errors or skipped tests. The Angular production build also passed. These checks exercise functional behavior, not production load or penetration resistance.',
 'The actual Nginx, Spring Boot and PostgreSQL stack': 'The updated Nginx, Spring Boot and Oracle DB stack passed the API walkthrough on localhost port 4301. It created a venue and event, confirmed seats, rejected duplicate sales, checked revenue, cancelled and rebooked seats, and checked in the guest. Logs distinguish these Oracle checks from the earlier PostgreSQL demonstration.',
 'The Docker smoke checks used a separate running PostgreSQL dataset': 'Screenshots 01 to 13 document a local H2 session. Screenshot 14 records the earlier PostgreSQL demonstration, while screenshot 15 shows the updated Oracle-backed application. The separate datasets explain different counts and totals. Oracle is the required database for project P_014; historical verification evidence is retained with its original database labels.',
 '[5] PostgreSQL 17. Constraints.': '[5] Oracle Free container maintainer. Database setup. https://github.com/gvenzl/oci-oracle-free',
 'Documentation consulted on 24 November': 'Documentation consulted on 24 November 2026. Dependency files identify the implemented versions. Oracle container setup follows the maintainer documentation [5]. The Java runtime choice meets the Spring Boot 3.5 requirements [2].',
}
for el in list(body)[cut:]:
    for p in el.iter(tag('p')):
        old=text(p); replacement=next((v for k,v in special.items() if old.startswith(k)),None)
        if replacement:settext(p,replacement);continue
        for t in p.iter(tag('t')):
            if t.text:
                t.text=t.text.replace('PostgreSQL 17 Alpine','Oracle Database Free').replace('PostgreSQL 17','Oracle Database Free').replace('PostgreSQL','Oracle DB').replace('db:5432','db:1521/FREEPDB1').replace('/var/lib/postgresql/data','/opt/oracle/oradata')
                t.text=t.text.replace('Twelve backend integration tests passed,','Twelve backend integration tests passed on H2 and Oracle,')
# Correct contents after the student's cover moved the abstract to page 2.
toc=next(x for x in body if x.tag==tag('tbl'))
for row in list(toc)[2:]:
    if row.tag!=tag('tr'):continue
    cells=row.findall('w:tc',NS)
    if len(cells)==3 and text(cells[2]).isdigit():settext(cells[2],str(int(text(cells[2]))+1))
rows=toc.findall('w:tr',NS)
for number,title,page in [('11','Project registration and Oracle database','15'),('12','Continuous integration and deployment','16')]:
    row=deepcopy(rows[-1]);cells=row.findall('w:tc',NS)
    for c,value in zip(cells,[number,title,page]):settext(c,value)
    toc.append(row)

blocks=[breakpage(),newp('Project registration and Oracle database',heading1),
 newp('Project P_014 | Java Batch 4 | Full Stack Development | Media and Entertainment'),
 newp('Registered project scope',heading2),
 newp('VenueVista EventPro Ticketing and Venue Management covers event ticketing and venue operations with seating charts, ticket sales and sales analytics. Its registered stack is Java, Spring Boot, Angular and Oracle DB, with event and media industry familiarity. The organizer workflow reflects this domain through venue capacity, event schedules, guest admission and confirmed-sales reporting.'),
 newp('Oracle database implementation',heading2),
 newp('The primary Docker database is Oracle Database Free, using the maintained gvenzl/oracle-free:23-slim image. The API includes the ojdbc11 JDBC driver and connects to jdbc:oracle:thin:@//db:1521/FREEPDB1 as the venuevista application user. A dedicated volume persists files under /opt/oracle/oradata. The database health check uses healthcheck.sh. Local development can still use H2.'),
 newp('Validation and data separation',heading2),
 newp('The same 12 integration tests pass on H2 and on an isolated venuevista_test Oracle schema, including the two-buyer seat contention case. Test configuration uses TEST_DB_URL, TEST_DB_USER and TEST_DB_PASSWORD. Tests create and drop their schema objects, so test variables must never reference an application schema. The running Oracle application also passed the full ticket lifecycle smoke checks.'),
 newp('Existing demonstration records',heading2),
 newp('The earlier PostgreSQL data volume is retained separately and is not converted automatically into Oracle. A fresh Oracle application schema receives the demonstration seed data. Historical screenshots and verification logs retain their database labels; the latest Oracle screenshot and logs provide evidence for the registered technology requirement.'),
 newp('Starting the updated project',heading2),
 newp('Run docker compose up --build -d from the project directory. Oracle initialization may take several minutes. Default host ports are 4200 for the frontend and 8080 for the API; API_PORT and UI_PORT provide overrides. The verification environment uses 8091 and 4301. See README.md and docs/PROJECT.md for setup and registration details.'),
 breakpage(),newp('Continuous integration and deployment',heading1),
 newp('The GitHub Actions workflow is .github/workflows/ci-cd.yml. Pull requests, main-branch pushes and manual dispatch run Java 21 tests, Oracle database tests, and the Angular build on Node.js 22. Docker images are built only after those checks pass. Official Actions use verified commit references; test results and the compiled frontend are uploaded as artifacts.'),
 newp('Release and deployment flow',heading2),
 newp('A successful main-branch run publishes backend and frontend images to GitHub Container Registry using matching sha-<full-commit> tags. Pull requests do not publish images or use deployment secrets. An enabled staging job transfers the Compose definition and deployment helpers over SSH, using a verified server host key. It deploys the same tested image pair.'),
 newp('Staging configuration',heading2),
 newp('Create a staging environment and configure SSH_HOST, SSH_USER, SSH_PRIVATE_KEY and SSH_KNOWN_HOSTS. Optional variables set SSH_PORT and DEPLOY_DIR. The repository variable ENABLE_STAGING_DEPLOY=true enables automatic deployment after CI. Database passwords stay in the server .env file. Private GHCR packages require a read-only registry login on the server. The server needs Docker Compose, Bash, curl, Python 3 and flock.'),
 newp('Readiness and rollback',heading2),
 newp('The deployment script locks the staging directory, pulls the image pair and waits for database, API and frontend health checks. A read-only probe confirms the Angular page, API and database through Nginx. Release files record the current and previous image identities. A failed rollout attempts to restore the previous pair and exits with failure. It preserves the Oracle volume; rollback does not reverse schema changes or guarantee uninterrupted service.'),
 newp('Scope and verification status',heading2),
 newp('Staging is loopback-only and accessed through an SSH tunnel because the academic console has no login. Workflow syntax and local build checks have been validated. Hosted GitHub execution and remote deployment require pushing to a repository and configuring the staging server and secrets. The full setup, activation and rollback instructions are in docs/CI-CD.md.'),
 newp('GitHub references',heading2),
 newp('Container publication: https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images'),
 newp('Deployment environments: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments')]
sect=body.find('w:sectPr',NS);insert_at=list(body).index(sect) if sect is not None else len(body)
for offset,p in enumerate(blocks):body.insert(insert_at+offset,p)
assert [E.tostring(x) for x in list(body)[:cut]]==cover_before
# Replace only the architecture diagram in an existing relationship.
im=Image.new('RGB',(2000,840),'white');d=ImageDraw.Draw(im)
f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';fb='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
for x,y,w,h,title,lines in [
(30,65,540,270,'Angular frontend',['Standalone components','Forms and seat selection','Charts and CSV export']),
(730,65,540,270,'Spring Boot API',['REST and validation','Transactional booking service','JPA repositories and ojdbc11']),
(1470,65,490,270,'Oracle DB Free',['Events and venues','Booking history','Active seat inventory']),
(380,530,1210,245,'Docker Compose',['Nginx serves Angular and forwards /api to the backend','Spring Boot connects to db:1521/FREEPDB1','A named volume preserves Oracle database files'])]:
 d.rounded_rectangle((x,y,x+w,y+h),14,fill='#f8f6fc',outline='#bba9d6',width=3)
 d.text((x+25,y+24),title,font=ImageFont.truetype(fb,37),fill='#211b2c')
 for i,line in enumerate(lines):d.text((x+25,y+85+i*43),line,font=ImageFont.truetype(f,27),fill='#5c4e6b')
for a,b,c,e,label in [(570,200,730,200,'JSON'),(1270,200,1470,200,'JDBC')]:
 d.line((a,b,c,e),fill='#9184a5',width=5);d.polygon([(c,e),(c-17,e-10),(c-17,e+10)],fill='#9184a5');d.text(((a+c)//2-50,b-45),label,font=ImageFont.truetype(f,26),fill='#5b4e6a')
d.line((1000,335,1000,530),fill='#9184a5',width=5);d.polygon([(1000,530),(990,513),(1010,513)],fill='#9184a5')
diagram=ROOT/'docs/architecture.png';im.save(diagram)
updated={'word/document.xml':E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True),'word/media/image1.png':diagram.read_bytes()}
temp=path.with_suffix('.updating.docx')
with ZipFile(temp,'w',ZIP_DEFLATED) as z:
 for name,(info,data) in entries.items():z.writestr(info,updated.get(name,data))
temp.replace(path)
proof={'coverElementsPreserved':cut,'coverXmlSha256':hashlib.sha256(b''.join(cover_before)).hexdigest(),'unchangedPackageParts':len(entries)-len(updated),'note':'First page body XML and all existing styles, relationships and header/footer parts retained.'}
(ROOT/'verification/report-cover-preservation.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Updated report body; preserved',cut,'cover elements.')
