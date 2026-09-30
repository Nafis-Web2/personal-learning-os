"use client";
import {useEffect,useState} from "react";
import {api,DEV_USER} from "../lib/api";
export default function IntegrationStatus(){
 const [next,setNext]=useState<any>(null),[status,setStatus]=useState<any>(null);
 useEffect(()=>{api.integration().then(setStatus).catch(()=>{});if(DEV_USER)api.next(DEV_USER).then(setNext).catch(()=>{})},[]);
 return <div className="card"><div className="eyebrow">UNIFIED LEARNING ENGINE</div><h3>{next?.next_action?.replaceAll("_"," ")||"Preparing your next action"}</h3><p className="muted">{status?`${status.systems.length} learning systems connected · ${status.mock_ai?"AI provider still in safe mock mode":"Live AI connected"}`:"Checking backend…"}</p></div>
}
