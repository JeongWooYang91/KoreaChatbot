import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../context/UserContext";

const visaOptions = ["C4", "D2", "D3", "D4", "D10", "E4", "E7", "E8", "E9", "H2", "F1", "F2", "F3", "F4", "F6", "G1", "Others"];

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
    workExperience: "",
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

    const userInfo = {
      Name: form.name,
      Nationality: form.nationality,
      NativeLanguage: form.nativeLanguage,
      "Living in Korea": form.livingInKorea,
      "Duration of Stay": form.livingInKorea === "Yes" ? form.stayDuration : "n/a",
      "Visa Type": form.visaType === "Others" ? form.customVisa : form.visaType,
      Industry: form.industry,
      "Work Experience": form.workExperience,
      "Korean Test Score": form.koreanTestScore,
      "Duration of Korean Study": form.koreanStudyDuration,
      Interests: form.interests,
      Hobbies: form.hobbies,
    };

    setUserInfo(userInfo);
    navigate("/scenarios");
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-3"><input className="form-control" name="name" placeholder="Name" value={form.name} onChange={handleChange} /></div>
      <div className="mb-3"><input className="form-control" name="nationality" placeholder="Nationality" value={form.nationality} onChange={handleChange} /></div>
      <div className="mb-3"><input className="form-control" name="nativeLanguage" placeholder="Native Language" value={form.nativeLanguage} onChange={handleChange} /></div>

      <div className="mb-3">
        <label>Do you live in Korea?</label>
        <select className="form-select" name="livingInKorea" value={form.livingInKorea} onChange={handleChange}>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
      </div>

      {form.livingInKorea === "Yes" && (
        <div className="mb-3"><input className="form-control" name="stayDuration" placeholder="Stay Duration" value={form.stayDuration} onChange={handleChange} /></div>
      )}

      <div className="mb-3">
        <label>Visa Type</label>
        <select className="form-select" name="visaType" value={form.visaType} onChange={handleChange}>
          {visaOptions.map((v) => <option key={v}>{v}</option>)}
        </select>
      </div>

      {form.visaType === "Others" && (
        <div className="mb-3"><input className="form-control" name="customVisa" placeholder="Enter Visa Type" value={form.customVisa} onChange={handleChange} /></div>
      )}

      <div className="mb-3"><input className="form-control" name="industry" placeholder="Industry" value={form.industry} onChange={handleChange} /></div>
      <div className="mb-3"><input className="form-control" name="workExperience" placeholder="Work Experience" value={form.workExperience} onChange={handleChange} /></div>
      <div className="mb-3"><input className="form-control" name="koreanTestScore" placeholder="Korean Test Score" value={form.koreanTestScore} onChange={handleChange} /></div>
      <div className="mb-3"><input className="form-control" name="koreanStudyDuration" placeholder="Duration of Korean Study" value={form.koreanStudyDuration} onChange={handleChange} /></div>
      <div className="mb-3"><input className="form-control" name="interests" placeholder="Interests" value={form.interests} onChange={handleChange} /></div>
      <div className="mb-3"><input className="form-control" name="hobbies" placeholder="Hobbies" value={form.hobbies} onChange={handleChange} /></div>

      <div className="form-check mb-3">
        <input className="form-check-input" type="checkbox" name="agree" checked={form.agree} onChange={handleChange} />
        <label className="form-check-label">📜 Consent for Data Collection</label>
      </div>

      <button type="submit" className="btn btn-success">Submit</button>
    </form>
  );
};

export default UserInfoForm;