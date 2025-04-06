import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../context/UserContext";

const visaOptions = ["C4", "D2", "D3", "D4", "D10", "E4", "E7", "E8", "E9", "H2", "F1", "F2", "F3", "F4", "F6", "G1", "Others"];
const nationalityOptions = ["USA", "Canada", "India", "Indonesia", "Philippines", "Vietnam", "China", "Japan", "Germany", "France", "Other"];
const languageOptions = ["English", "Spanish", "Mandarin", "Korean", "Japanese", "Vietnamese", "Indonesian", "Tagalog", "Other"];
const industryOptions = ["IT", "Education", "Healthcare", "Finance", "Hospitality", "Manufacturing", "Other"];

const UserInfoForm = () => {
  const [form, setForm] = useState({
    name: "",
    nationality: "",
    nativeLanguage: "",
    livingInKorea: "No",
    stayDuration: "",
    visaType: "",
    customVisa: "",
    industry: "",
    workExperience: 0,
    koreanTestScore: "",
    koreanStudyDuration: "",
    interests: "",
    hobbies: "",
    agree: true,
  });

  const navigate = useNavigate();
  const { setUserInfo } = useUser();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.agree) return;

    const visaType = form.visaType === "Others" ? form.customVisa : form.visaType;

    const userInfo = {
      Name: form.name,
      Nationality: form.nationality,
      NativeLanguage: form.nativeLanguage,
      Living_in_Korea: form.livingInKorea,
      Duration_of_Stay: form.livingInKorea === "Yes" ? form.stayDuration : "n/a",
      Visa_Type: visaType,
      Industry: form.industry,
      Work_Experience: form.workExperience,
      Korean_Test_Score: form.koreanTestScore,
      Duration_of_Korean_Study: form.koreanStudyDuration,
      Interests: form.interests,
      Hobbies: form.hobbies,
    };

    console.log("User Info Submitted:", userInfo);
    setUserInfo(userInfo);
    navigate("/scenarios");
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-3">
        <input className="form-control" name="name" placeholder="Name" value={form.name} onChange={handleChange} />
      </div>

      <div className="mb-3">
        <label>Nationality</label>
        <select className="form-select" name="nationality" value={form.nationality} onChange={handleChange}>
          <option value="">Select nationality</option>
          {nationalityOptions.map((n) => <option key={n}>{n}</option>)}
        </select>
      </div>

      <div className="mb-3">
        <label>Native Language</label>
        <select className="form-select" name="nativeLanguage" value={form.nativeLanguage} onChange={handleChange}>
          <option value="">Select language</option>
          {languageOptions.map((lang) => <option key={lang}>{lang}</option>)}
        </select>
      </div>

      <div className="mb-3">
        <label>Do you live in Korea?</label><br />
        <div className="form-check form-check-inline">
          <input className="form-check-input" type="radio" name="livingInKorea" value="Yes" checked={form.livingInKorea === "Yes"} onChange={handleChange} />
          <label className="form-check-label">Yes</label>
        </div>
        <div className="form-check form-check-inline">
          <input className="form-check-input" type="radio" name="livingInKorea" value="No" checked={form.livingInKorea === "No"} onChange={handleChange} />
          <label className="form-check-label">No</label>
        </div>
      </div>

      {form.livingInKorea === "Yes" && (
        <div className="mb-3">
          <label>Stay Duration</label>
          <select className="form-select" name="stayDuration" value={form.stayDuration} onChange={handleChange}>
            <option value="">Select duration</option>
            <option>Less than 6 months</option>
            <option>6 months – 1 year</option>
            <option>1–2 years</option>
            <option>2–5 years</option>
            <option>5+ years</option>
          </select>
        </div>
      )}

      <div className="mb-3">
        <label>Visa Type</label>
        <select className="form-select" name="visaType" value={form.visaType} onChange={handleChange}>
          {visaOptions.map((v) => <option key={v}>{v}</option>)}
        </select>
      </div>

      {form.visaType === "Others" && (
        <div className="mb-3">
          <input className="form-control" name="customVisa" placeholder="Enter Visa Type" value={form.customVisa} onChange={handleChange} />
        </div>
      )}

      <div className="mb-3">
        <label>Industry</label>
        <select className="form-select" name="industry" value={form.industry} onChange={handleChange}>
          <option value="">Select industry</option>
          {industryOptions.map((i) => <option key={i}>{i}</option>)}
        </select>
      </div>

      <div className="mb-3">
        <label htmlFor="workExperienceSlider">Work Experience (Years): {form.workExperience}</label>
        <input type="range" className="form-range" min="0" max="20" step="1" name="workExperience"
          value={form.workExperience} onChange={handleChange} id="workExperienceSlider" />
      </div>

      <div className="mb-3">
        <input className="form-control" name="koreanTestScore" placeholder="Korean Test Score (optional)" value={form.koreanTestScore} onChange={handleChange} />
      </div>

      <div className="mb-3">
        <label>Korean Study Duration</label>
        <select className="form-select" name="koreanStudyDuration" value={form.koreanStudyDuration} onChange={handleChange}>
          <option value="">Select study duration</option>
          <option>Less than 6 months</option>
          <option>6 months – 1 year</option>
          <option>1–2 years</option>
          <option>2–5 years</option>
          <option>5+ years</option>
        </select>
      </div>

      <div className="mb-3">
        <input className="form-control" name="interests" placeholder="Interests (e.g., Travel, Food)" value={form.interests} onChange={handleChange} />
      </div>

      <div className="mb-3">
        <input className="form-control" name="hobbies" placeholder="Hobbies (e.g., Soccer, Reading)" value={form.hobbies} onChange={handleChange} />
      </div>

      <div className="form-check mb-3">
        <input className="form-check-input" type="checkbox" name="agree" checked={form.agree} onChange={handleChange} />
        <label className="form-check-label">📜 Consent for Data Collection</label>
      </div>

      <button type="submit" className="btn btn-success">Submit</button>
    </form>
  );
};

export default UserInfoForm;
