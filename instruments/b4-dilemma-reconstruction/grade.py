#!/usr/bin/env python3
"""B4.4 grade.py — per-item distributions and policy/physical ratio.

Physical  := settling_test names a measurement or physical derivation.
Policy    := settling_test names a decision, statute, funding rule, or procedure.
Unresolved := neither read is supported.

The split is derived from settling_test text; no extra field is asked.
"""

import json
import sys
from collections import Counter, defaultdict

P_KWS = ("measure,measurement,weigh,meter,gauge,sensor,read,calculate,"
         "derive,physics,physical,mass,force,energy,temperature,pressure,"
         "flow,velocity,density,volume,length,test,experiment,observation,"
         "data,instrument,device,scale,thermometer,barometer,accelerometer,"
         "gps,coordinate,dimension,tolerance,calibration,verification,"
         "survey,assay,analysis,sample,composition,viscosity,hardness,"
         "tensile,friction,coefficient,equation,formula,law,newton,ohm,"
         "watt,joule,pascal,kelvin,si unit,gram,kilogram,newton,meter,"
         "liter,area,perimeter,diameter,angle,vector,field,gradient,"
         "flux,potential,kinetic,work,power,torque,momentum,frequency,"
         "wavelength,amplitude,phase,hertz,decibel,spectrum,radiation,"
         "reaction,oxidation,acid,ph,conductivity,resistivity,impedance,"
         "capacitance,inductance,current,voltage,resistance,signal,noise,"
         "entropy,bit,latency,error,uncertainty,precision,accuracy,"
         "resolution,sensitivity,repeatability,stability,reliability,"
         "fatigue,corrosion,wear,probability,statistics,mean,variance,"
         "standard deviation,confidence,hypothesis,correlation,regression,"
         "simulation,model,finite element,monte carlo,stochastic,chaos,"
         "phase transition,boiling,melting,diffusion,permeability,porosity,"
         "ionization,excitation,fluorescence,piezoelectric,ferromagnetic,"
         "superconducting,plasma,planck,stefan-boltzmann,beer-lambert,"
         "photoelectric,semiconductor,diode,transistor,adc,dac,oscillator,"
         "crystal,filter,amplifier,modulator,detector,integrator,"
         "logarithm,exponential,trigonometric,elliptic,spherical,"
         "cartesian,polar,parametric,implicit,explicit").split(",")

S_KWS = ("decision,decide,policy,statute,law,regulation,code,rule,"
         "procedure,protocol,funding,budget,allocate,approve,authorize,"
         "mandate,requirement,standard,guideline,directive,order,vote,"
         "committee,board,agency,department,compliance,legislation,act,"
         "bill,ordinance,bylaw,charter,constitution,treaty,agreement,"
         "contract,memorandum,warranty,guarantee,liability,insurance,"
         "premium,coverage,claim,settlement,litigation,arbitration,"
         "mediation,negotiation,collective,union,association,organization,"
         "corporation,company,firm,partnership,llc,inc,ltd,nonprofit,"
         "foundation,trust,endowment,grant,scholarship,salary,wage,"
         "compensation,pension,retirement,401k,medicare,medicaid,"
         "subsidy,tariff,tax,duty,levy,fine,penalty,sanction,embargo,"
         "quota,license,permit,certification,accreditation,credential,"
         "qualification,eligibility,entitlement,right,privilege,immunity,"
         "exemption,waiver,appeal,review,hearing,inquiry,investigation,"
         "audit,inspection,examination,assessment,evaluation,appraisal,"
         "oversight,supervision,monitoring,surveillance,control,governance,"
         "management,administration,operation,implementation,enforcement,"
         "prosecution,defense,adjudication,sentencing,parole,probation,"
         "incarceration,detention,custody,bail,bond,subpoena,summons,"
         "warrant,indictment,verdict,judgment,decree,injunction,ban,"
         "prohibition,restriction,limitation,constraint,condition,"
         "stipulation,provision,clause,article,section,amendment,"
         "revision,update,appendix,schedule,annex,attachment,endorsement,"
         "release,discharge,acquittal,pardon,clemency,expungement,"
         "confidentiality,classification,privacy,gdpr,hipaa,foia,"
         "transparency,accountability,responsibility,fiduciary,trustee,"
         "guardian,executor,administrator,agent,proxy,attorney,counsel,"
         "advocate,ombudsman,mediator,arbitrator,judge,magistrate,referee,"
         "commissioner,hearing officer,tribunal,court,jury,coroner,"
         "sheriff,marshal,clerk,recorder,notary,justice,mayor,council,"
         "commission,board of supervisors,city council,state legislature,"
         "congress,parliament,committee,office,division,branch,section,"
         "unit,team,squad,crew,shift,platoon,company,battalion,regiment,"
         "brigade,division,corps,army,fleet,wing,group,squadron,task force,"
         "peacekeeping,humanitarian,relief,assistance,aid,development,"
         "cooperation,partnership,alliance,coalition,confederation,federation,"
         "union,republic,commonwealth,territory,protectorate,colony,lease,"
         "concession,cession,annexation,independence,sovereignty,autonomy,"
         "home rule,devolution,decentralization,privatization,nationalization,"
         "expropriation,eminent domain,condemnation,appropriation,allocation,"
         "reallocation,redistribution,transfer,conveyance,assignment,"
         "delegation,procurement,acquisition,purchase,sale,rental,hire,"
         "employment,engagement,retention,appointment,nomination,election,"
         "selection,recruitment,hiring,firing,termination,dismissal,removal,"
         "suspension,disciplinary,grievance,conciliation,fact-finding,"
         "recommendation,advisory,opinion,ruling,holding,precedent,"
         "stare decisis,en banc,panel,magistrate,special master,monitor,"
         "receiver,conservator,guardian ad litem,amicus,intervenor,"
         "participant,stakeholder,party,plaintiff,defendant,petitioner,"
         "respondent,appellant,appellee,cross-claimant,counter-claimant,"
         "third-party,class action,derivative,qui tam,habeas corpus,mandamus,"
         "certiorari,quo warranto,collateral,direct,appeal,review,rehearing,"
         "sua sponte,ex parte,in camera,under seal,confidential,privileged,"
         "work product,attorney-client,doctor-patient,journalist,source,"
         "whistleblower,informant,classified,secret,top secret,clearance,"
         "background check,vetting,screening,polygraph,interview,interrogation,"
         "deposition,discovery,disclosure,production,inspection,interrogatory,"
         "request,subpoena,summons,notice,service,process,jurisdiction,venue,"
         "forum,choice of law,conflict of laws,recognition,enforcement,"
         "full faith and credit,comity,extradition,rendition,change of venue,"
         "severance,bifurcation,consolidation,joinder,impleader,interpleader,"
         "intervention,substitution,replacement,successor,assignee,transferee,"
         "legatee,devisee,heir,beneficiary,claimant,creditor,debtor,obligor,"
         "obligee,principal,surety,guarantor,indemnitor,indemnitee,insured,"
         "insurer,underwriter,reinsurer,broker,agent,adjuster,actuary,"
         "surveyor,appraiser,assessor,collector,auditor,examiner,investigator,"
         "inspector,monitor,evaluator,reviewer,consultant,advisor,counselor,"
         "strategist,planner,coordinator,facilitator,moderator,chair,president,"
         "vice president,secretary,treasurer,comptroller,controller,chief,"
         "officer,director,manager,supervisor,foreman,superintendent,"
         "administrator,commissioner,chairperson,spokesperson,representative,"
         "delegate,envoy,ambassador,consul,attaché,chargé d'affaires,"
         "plenipotentiary,emissary,messenger,courier,diplomat,negotiator,"
         "conciliator,umpire,referee,justice,chancellor,master,prothonotary,"
         "clerk,registrar,recorder,custodian,keeper,warden,ranger,guardian,"
         "protector,defender,advocate,champion,patron,sponsor,underwriter,"
         "backer,supporter,proponent,proposer,mover,seconder,introducer,"
         "presenter,referrer,nominator,designator,appointer,elector,voter,"
         "constituent,citizen,resident,inhabitant,occupant,tenant,leaseholder,"
         "freeholder,landowner,property owner,titleholder,mortgagor,mortgagee,"
         "lienholder,secured party,borrower,lender,investor,shareholder,"
         "stockholder,bondholder,policyholder,annuitant,pensioner,retiree,"
         "employee,employer,worker,laborer,craftsman,artisan,tradesperson,"
         "journeyman,apprentice,trainee,intern,volunteer,conscript,draftee,"
         "enlistee,recruit,cadet,midshipman,officer,noncommissioned,warrant,"
         "specialist,technician,operator,mechanic,engineer,architect,designer,"
         "planner,surveyor,inspector,tester,analyst,researcher,scientist,"
         "scholar,academic,educator,instructor,professor,teacher,tutor,mentor,"
         "coach,trainer,advisor,counselor,therapist,clinician,practitioner,"
         "provider,supplier,vendor,contractor,subcontractor,consultant,"
         "freelancer,independent,sole proprietor,entrepreneur,founder,owner,"
         "partner,member,director,trustee,fiduciary,custodian,guardian,"
         "conservator,receiver,liquidator,trustee in bankruptcy,debtor in possession,"
         "committee,creditors,equity,security,holders,claimants,intervenors,"
         "parties in interest").split(",")


def classify(text):
    t = text.lower()
    p_score = sum(1 for kw in P_KWS if kw in t)
    s_score = sum(1 for kw in S_KWS if kw in t)
    if p_score > 0 and s_score == 0:
        return "physical"
    if s_score > 0 and p_score == 0:
        return "policy"
    return "unresolved"


def grade(req_path, out_path):
    items = defaultdict(list)
    with open(req_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            items[row["item_id"]].append(row)

    results = []
    for iid, reqs in sorted(items.items()):
        status_dist = Counter(r["status"] for r in reqs)
        layer_dist = Counter(r["layer"] for r in reqs)
        physical = policy = unresolved = 0
        for r in reqs:
            c = classify(r["settling_test"])
            if c == "physical":
                physical += 1
            elif c == "policy":
                policy += 1
            else:
                unresolved += 1
        total = len(reqs)
        ratio = f"{physical}:{policy}" if (physical + policy) > 0 else "N/A"
        results.append(
            {
                "item_id": iid,
                "requirement_count": total,
                "status_distribution": dict(status_dist),
                "layer_distribution": dict(layer_dist),
                "physical_count": physical,
                "policy_count": policy,
                "unresolved_count": unresolved,
                "policy_to_physical_ratio": ratio,
            }
        )

    with open(out_path, "w", encoding="utf-8") as fh:
        for res in results:
            fh.write(json.dumps(res, ensure_ascii=False) + "\n")

    print(f"Graded {len(results)} items")


# ---- run-record wiring (added; logic above is unchanged) --------------------
import os  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402


def _rows(path):
    try:
        return sum(1 for _ in runrecord.read_jsonl(path))
    except (OSError, ValueError):
        return None


def _status_by_rows(path):
    n = _rows(path)
    return ("ok" if n else "empty"), {"rows": n}, ""

def main(argv):
    if len(argv) != 3:
        print("Usage: grade.py <requirements.jsonl> <grades.jsonl>", file=sys.stderr)
        return 1

    def body():
        grade(argv[1], argv[2])
        return _status_by_rows(argv[2])
    return runrecord.run("b4/grade.py", argv[1:], None, [argv[1]], argv[2], body)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
