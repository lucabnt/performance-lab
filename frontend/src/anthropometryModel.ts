type Measurement={weight_kg?:unknown;height_cm?:unknown};

/** Descriptive kg/m² from one record only; never borrow another date's height. */
export function bodyMassIndex(measurement:Measurement):number|null{
 const {weight_kg:weight,height_cm:height}=measurement;
 if(typeof weight!=='number'||typeof height!=='number'||!Number.isFinite(weight)||!Number.isFinite(height)||weight<=0||height<=0)return null;
 const value=weight/(height/100)**2;
 return Number.isFinite(value)?value:null;
}
