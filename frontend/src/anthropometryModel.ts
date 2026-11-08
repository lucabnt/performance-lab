type Measurement={weight_kg?:unknown;height_cm?:unknown;perineal_height_cm?:unknown};

/** Descriptive kg/mÂ² from one record only; never borrow another date's height. */
export function bodyMassIndex(measurement:Measurement):number|null{
 const {weight_kg:weight,height_cm:height}=measurement;
 if(typeof weight!=='number'||typeof height!=='number'||!Number.isFinite(weight)||!Number.isFinite(height)||weight<=0||height<=0)return null;
 const value=weight/(height/100)**2;
 return Number.isFinite(value)?value:null;
}

/** Descriptive percentage from the same observation; never merge records. */
export function perinealHeightRatio(measurement:Measurement):number|null{
 const {perineal_height_cm:perineal,height_cm:height}=measurement;
 if(typeof perineal!=='number'||typeof height!=='number'||!Number.isFinite(perineal)||!Number.isFinite(height)||perineal<=0||height<=0||perineal>=height)return null;
 return 100*perineal/height;
}
