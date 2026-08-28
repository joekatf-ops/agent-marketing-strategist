import { readFileSync } from "node:fs";

// Deterministic Draft 2020-12 subset used by the intake schema. The governed
// date and IANA-timezone format assertions are deliberately active here.

function canonical(value) {
  if (Array.isArray(value)) {
    return `[${value.map(canonical).join(",")}]`;
  }
  if (value !== null && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function equal(left, right) {
  return canonical(left) === canonical(right);
}

function resolveReference(root, reference) {
  if (!reference.startsWith("#/")) {
    throw new Error(`unsupported schema reference: ${reference}`);
  }
  return reference
    .slice(2)
    .split("/")
    .map((part) => decodeURIComponent(part).replaceAll("~1", "/").replaceAll("~0", "~"))
    .reduce((value, part) => value[part], root);
}

function matchesType(instance, type) {
  switch (type) {
    case "null":
      return instance === null;
    case "object":
      return instance !== null && typeof instance === "object" && !Array.isArray(instance);
    case "array":
      return Array.isArray(instance);
    case "string":
      return typeof instance === "string";
    case "integer":
      return typeof instance === "number" && Number.isInteger(instance);
    case "number":
      return typeof instance === "number" && Number.isFinite(instance);
    case "boolean":
      return typeof instance === "boolean";
    default:
      throw new Error(`unsupported schema type: ${type}`);
  }
}

function isCalendarDate(value) {
  const match = /^([0-9]{4})-([0-9]{2})-([0-9]{2})$/.exec(value);
  if (match === null) {
    return false;
  }
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  if (year < 1 || month < 1 || month > 12) {
    return false;
  }
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  return day >= 1 && day <= days[month - 1];
}

function isIanaTimezone(value) {
  try {
    new Intl.DateTimeFormat("en-US", { timeZone: value }).format(0);
    return true;
  } catch (error) {
    if (error instanceof RangeError) {
      return false;
    }
    throw error;
  }
}

function validate(instance, schema, root, path = "$") {
  if (schema === true) {
    return [];
  }
  if (schema === false) {
    return [`${path} is rejected by a false schema`];
  }

  const errors = [];
  if (schema.$ref !== undefined) {
    errors.push(...validate(instance, resolveReference(root, schema.$ref), root, path));
  }

  if (schema.oneOf !== undefined) {
    const matches = schema.oneOf.filter(
      (subschema) => validate(instance, subschema, root, path).length === 0,
    ).length;
    if (matches !== 1) {
      errors.push(`${path} must match exactly one schema`);
    }
  }
  for (const subschema of schema.allOf ?? []) {
    errors.push(...validate(instance, subschema, root, path));
  }
  if (schema.if !== undefined) {
    const branch = validate(instance, schema.if, root, path).length === 0 ? "then" : "else";
    if (schema[branch] !== undefined) {
      errors.push(...validate(instance, schema[branch], root, path));
    }
  }

  if (schema.const !== undefined && !equal(instance, schema.const)) {
    errors.push(`${path} does not equal the required constant`);
  }
  if (schema.enum !== undefined && !schema.enum.some((candidate) => equal(instance, candidate))) {
    errors.push(`${path} is not in the allowed enum`);
  }

  if (schema.type !== undefined) {
    const allowed = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!allowed.some((type) => matchesType(instance, type))) {
      return [...errors, `${path} has the wrong type`];
    }
  }

  if (instance !== null && typeof instance === "object" && !Array.isArray(instance)) {
    for (const required of schema.required ?? []) {
      if (!Object.hasOwn(instance, required)) {
        errors.push(`${path}.${required} is required`);
      }
    }
    const properties = schema.properties ?? {};
    const additional = schema.additionalProperties ?? true;
    for (const [key, value] of Object.entries(instance)) {
      const childPath = `${path}.${key}`;
      if (Object.hasOwn(properties, key)) {
        errors.push(...validate(value, properties[key], root, childPath));
      } else if (additional === false) {
        errors.push(`${childPath} is not allowed`);
      } else if (typeof additional === "object") {
        errors.push(...validate(value, additional, root, childPath));
      }
    }
    if (Object.keys(instance).length < (schema.minProperties ?? 0)) {
      errors.push(`${path} has too few properties`);
    }
    if (schema.propertyNames !== undefined) {
      for (const key of Object.keys(instance)) {
        errors.push(...validate(key, schema.propertyNames, root, `${path} property name ${key}`));
      }
    }
  }

  if (Array.isArray(instance)) {
    if (instance.length < (schema.minItems ?? 0)) {
      errors.push(`${path} has too few items`);
    }
    if (schema.maxItems !== undefined && instance.length > schema.maxItems) {
      errors.push(`${path} has too many items`);
    }
    if (schema.uniqueItems === true) {
      const values = instance.map(canonical);
      if (new Set(values).size !== values.length) {
        errors.push(`${path} contains duplicate items`);
      }
    }
    if (schema.items !== undefined) {
      instance.forEach((value, index) => {
        errors.push(...validate(value, schema.items, root, `${path}[${index}]`));
      });
    }
  }

  if (typeof instance === "string") {
    if ([...instance].length < (schema.minLength ?? 0)) {
      errors.push(`${path} is too short`);
    }
    if (schema.pattern !== undefined && !new RegExp(schema.pattern, "u").test(instance)) {
      errors.push(`${path} does not match its ECMAScript pattern`);
    }
    if (schema.format === "date" && !isCalendarDate(instance)) {
      errors.push(`${path} is not an RFC 3339 calendar date`);
    }
    if (schema.format === "iana-timezone" && !isIanaTimezone(instance)) {
      errors.push(`${path} is not an IANA timezone`);
    }
  }

  if (typeof instance === "number" && schema.minimum !== undefined && instance < schema.minimum) {
    errors.push(`${path} is below its minimum`);
  }
  return errors;
}

const payload = JSON.parse(readFileSync(0, "utf8"));
const results = payload.instances.map((instance) => {
  const errors = validate(instance, payload.schema, payload.schema);
  return { valid: errors.length === 0, errors };
});
process.stdout.write(JSON.stringify(results));
